import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rich import print

from .game_engine import GameEngine
from .models import Game

class GameConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self):
        self.timer_task = None
        super().__init__()

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            try:
                raise Exception('Anonymous user tried to connect')
            finally:
                await self.close()
                print('Closing the connection for', user)
        else:
            await self.accept()
            print(user,'connected')

            self.game_id = self.scope['url_route']['kwargs']['game_id']
            self.game_obj = await self.get_game_by_id(self.game_id)

            self.game_room_name = self.game_obj.get_game_name()
       
            await self.channel_layer.group_add(
                self.game_room_name,
                self.channel_name
            )

            fen = self.game_obj.fen
            moves_list = self.game_obj.get_moves_list()
            data = await self.init_JSON()
            self.game_engine = GameEngine(fen, moves_list)

            await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await self.get_game_by_id(self.game_id)

        user = self.scope['user']
        fen = self.game_obj.fen
        moves_list = self.game_obj.get_moves_list()
        self.game_engine = GameEngine(fen, moves_list)
        type = msg['type']

        if type == 'move':
            color = await database_sync_to_async(self.game_obj.get_color)(user.username)
            if color != self.game_obj.get_turn():
                try:
                    raise Exception("Color of the player does not match game's current turn")
                finally:
                    print(color, self.game_obj.get_turn())

            p = msg['picked_id']
            t = msg['target_id']
            is_legal_flag, game_result, new_fen = self.game_engine.is_legal(p, t)

            if is_legal_flag == False:
                return
            elif game_result == 'promoting':
                turn = self.game_obj.get_turn()
                data = {
                    'type': 'promoting',
                    'p': p,
                    't': t,
                    'turn': turn
                }
                await self.send_json(data)
                return   
            else:
                await self.update_game(new_fen)

            if game_result != False:
                await self.endgame_wrapper(game_result)
                
            color = await database_sync_to_async(self.game_obj.get_color)(user.username)

            # color = self.game_obj.get_color(user.username)
            # django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
            # same line is used in connect() method but here it throws an exception, don't know why

            await self.move_wrapper(color)
            return

        if type == 'promotion':
            p = msg['p']
            t = msg['t']
            turn = msg['turn']
            piece = msg['piece']
            game_result, new_fen = self.game_engine.promotion_handler(p, t, piece, turn)
            await self.update_game(new_fen)
            if game_result != False:
                await self.endgame_wrapper(game_result)

            color = await database_sync_to_async(self.game_obj.get_color)(user.username)
            await self.move_wrapper(color)
            return

        if type == 'draw_offer':
            data = {
                'type': 'draw_offer',
                'sender_channel_name': self.channel_name
            }
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'draw_offer_broadcast',
                    'text': data
                }
            )
        if type == 'draw_accept':
            await self.endgame_wrapper('draw-mutual')
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'basic_broadcast',
                    'text': {
                        'type': 'draw_accept',
                    }
                }
            )
            return
        if type == 'draw_reject':
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'basic_broadcast',
                    'text': {
                        'type': 'draw_reset',
                    }
                }
            )
            return

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_room_name,
            self.channel_name
        )
        print('close_code:',close_code)

    

    async def basic_broadcast(self, event):
        data = event['text']
        await self.send_json(data)
    
    async def draw_offer_broadcast(self, event):
        data = event['text']
        if data['sender_channel_name'] != self.channel_name:
            await self.send_json(data)

    @database_sync_to_async
    def update_game(self, new_fen):
        game_obj = Game.objects.get(id=self.game_id)
        game_obj.fen = new_fen
        game_obj.moves_list += ';' + new_fen
        game_obj.save()
        self.game_obj = game_obj

    def get_usernames(self):
        return self.game_obj.player_white.username, self.game_obj.player_black.username 

    @database_sync_to_async
    def get_game_by_id(self, game_id):
        return Game.objects.select_related("player_white", "player_black").get(id=game_id)
    
    def move_JSON(self):
        fen = self.game_obj.fen
        turn = self.game_obj.get_turn()
        moves_list = self.game_obj.get_moves_list()
        data = {
            'type': 'move',
            'fen': fen,
            'turn': turn,
            'moves_list': moves_list
        }
        return data

    def endgame_JSON(self, game_result):
        fen = self.game_obj.fen
        turn = self.game_obj.get_turn()
        moves_list = self.game_obj.get_moves_list()
        data = {
            'type': 'endgame',
            'fen': fen,
            'turn': turn,
            'game_result': game_result,
            'moves_list': moves_list
        }
        return data

    async def init_JSON(self):
        user = str(self.scope['user'])
        fen = self.game_obj.fen
        turn = self.game_obj.get_turn()
        color = await database_sync_to_async(self.game_obj.get_color)(user)
        time_black = self.to_timer_format(self.game_obj.timer_black)
        time_white = self.to_timer_format(self.game_obj.timer_white)
        moves_list = self.game_obj.get_moves_list()
        data = {
            'type': 'init',
            'fen': fen,
            'color': color,
            'turn': turn,
            'time_black': time_black,
            'time_white': time_white,
            'moves_list': moves_list
        }
        return data

    def to_timer_format(self, seconds):
        s = seconds
        m = s//60
        s = s - m*60
        if m < 10:
            m = f'0{m}'
        if s < 10:
            s = f'0{s}'
        return f'{m}:{s}'

    def opposite_color(self, color):
        if color == 'black':
            return 'white'
        else:
            return 'black'

    async def end_game(self, game_result):
        game_obj = await self.get_game_by_id(self.game_id)
        game_obj.is_running = False
        game_obj.is_finished = True
        if game_result == 'whitewins':
            game_obj.winner = game_obj.player_white
            game_obj.endgame_cause = 'CHECKMATE'
        elif game_result == 'blackwins':
            game_obj.winner = game_obj.player_black
            game_obj.endgame_cause = 'CHECKMATE'
        elif game_result == 'draw-stalemate':
            game_obj.endgame_cause = 'STALEMATE'
        elif game_result == 'draw-3r':
            game_obj.endgame_cause = 'THREEFOLD REPETITION'
        elif game_result == 'draw-50m':
            game_obj.endgame_cause = '50 MOVES RULE'
        elif game_result == 'draw-mutual':
            game_obj.endgame_cause = 'MUTUAL AGREEMENT'
        await database_sync_to_async(game_obj.save)()
        self.game_obj = game_obj
        return

    def promotion_handler(self, p, t, piece, turn):
        self.game_obj.promotion_handler(p, t, piece, turn)

    @database_sync_to_async
    def get_game_by_usernames(self, username1, username2):
        return Game.objects.get_or_new(username1, username2)

    async def endgame_wrapper(self, game_result):
        await self.end_game(game_result)
        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'timer_stop_broadcast'
            }
        )
        data = self.endgame_JSON(game_result)
        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'basic_broadcast',
                'text': data
            }
        )
        return

    async def move_wrapper(self, color):
        # 'color' argument is color of the player which is moving

        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'timer_handler',
                'text': color
            }
        )
        data = self.move_JSON()
        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'basic_broadcast',
                'text': data
            }
        )
        return

    async def timer_handler(self, event):
        moving_color = event['text']
        username = self.scope['user'].username
        consumer_color = self.game_obj.get_color(username)
        if consumer_color == moving_color:
            if self.timer_task != None:
                asyncio.Task.cancel(self.timer_task)
                self.timer_task = None
        elif consumer_color == self.opposite_color(moving_color):
            if self.timer_task == None:
                self.timer_task = asyncio.create_task(self.timer_countdown(self.opposite_color(moving_color)))
            else:
                try:
                    raise Exception("Scheduled a timer task for a timer that's already running")
                finally:
                    print('self.timer_task:', self.timer_task)

    
    async def timer_countdown(self, color):
        timer = self.get_timer(color)
        while True:
            await asyncio.sleep(1)
            timer -= 1
            await database_sync_to_async(self.update_timer)(timer, color)
            timer_formatted = self.to_timer_format(timer)
            data = {
                'type': 'time',
                'time': timer_formatted,
                'timer_color': color
            }
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'basic_broadcast',
                    'text': data
                }
            )

    def update_timer(self, time, timer_color):
        game_obj = Game.objects.get(id=self.game_id)
        if timer_color == 'white':
            game_obj.timer_white = time
        elif timer_color == 'black':
            game_obj.timer_black = time
        else:
            try:
                raise Exception('Undefined timer color')
            finally:
                print('timer_color:', timer_color)
        game_obj.save()

    def get_timer(self, color):
        if color == 'white':
            timer = self.game_obj.timer_white
        else:
            timer = self.game_obj.timer_black
        return timer

    async def timer_stop_broadcast(self, event):
        if self.timer_task is not None:
            asyncio.Task.cancel(self.timer_task)

class InviteConsumer(AsyncJsonWebsocketConsumer):
    groups = ['invite_group']
    async def connect(self):
        await self.accept()

    async def receive_json(self, msg):
        msg['sender_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            'invite_group',
            {
                'type': 'invite_broadcast',
                'text': msg
            }
        )

    async def disconnect(self, close_code):
        print('close_code:',close_code)

    async def invite_broadcast(self, msg):
        msg = msg['text']
        if self.channel_name != msg['sender_channel_name']:
            await self.send_json(msg)

    async def invite_accept_broadcast(self, msg):
        msg = msg['text']
        await self.send_json(msg)
           
