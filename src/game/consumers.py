import asyncio
import json

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import JsonWebsocketConsumer
from channels.db import database_sync_to_async
from rich import print

from .game_engine import GameEngine
from .models import Game
from .views import get_game


class GameConsumer(AsyncJsonWebsocketConsumer):
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
            self.timer_task = None

            game_id = self.scope['url_route']['kwargs']['game_id']
            self.game_obj = await self.get_game_by_id(game_id)

            self.game_room_name = self.game_obj.get_game_name()
       
            await self.channel_layer.group_add(
                self.game_room_name,
                self.channel_name
            )

            fen = self.game_obj.fen
            turn = self.game_obj.get_turn()
            color = self.game_obj.get_color(user.username)
            moves_list = self.game_obj.get_moves_list()
            data = self.init_JSON()
            self.game_engine = GameEngine(fen, moves_list)

            if turn != color:
                self.timer_task = 'placeholder'

            await self.send_json(data)

    async def receive_json(self, content):
        game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await self.get_game_by_id(game_id)

        fen = self.game_obj.fen
        moves_list = self.game_obj.get_moves_list()
        self.game_engine = GameEngine(fen, moves_list)
        msg = content
        type = msg['type']

        if type == 'move':
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

            color = msg['color']
            color = self.opposite_color(color)
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
        if type == 'reset':
            color = msg['color']
            self.game_obj.vote_for_reset(color)
            if self.game_obj.check_for_reset() == True:
                await self.channel_layer.group_send(
                    self.game_room_name,
                    {
                        'type': 'timer_stop_broadcast'
                    }
                )
                new_game_id = await self.reset_handler()
                data = await self.reset_JSON(new_game_id)
                await self.channel_layer.group_send(
                    self.game_room_name,
                    {
                        'type': 'basic_broadcast',
                        'text': data
                    }
                )
            return
        if type == 'promotion':
            p = msg['p']
            t = msg['t']
            turn = msg['turn']
            piece = msg['piece']
            game_result, new_fen = self.game_engine.promotion_handler(p, t, piece, turn)
            await self.update_game(new_fen)
            if game_result != False:
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
            color = msg['turn']
            color = self.opposite_color(color)
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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_room_name,
            self.channel_name
        )
        print('close_code:',close_code)

    async def timer_handler(self, event):
        if self.timer_task is None:
            color = event['text']
            self.timer_task = asyncio.create_task(self.timer_countdown(color))
        elif self.timer_task == 'placeholder':
            self.timer_task = None
        else:
            asyncio.Task.cancel(self.timer_task)
            self.timer_task = None

    async def timer_countdown(self, color):
        timer = self.get_timer(color)
        while timer > 0:
            await asyncio.sleep(1)
            timer -= 1
            await self.update_timer(timer, color)
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

    def get_timer(self, color):
        if color == 'white':
            timer = self.game_obj.timer_white
        else:
            timer = self.game_obj.timer_black
        return timer

    async def basic_broadcast(self, event):
        data = event['text']
        await self.send_json(data)

    @database_sync_to_async
    def update_game(self, new_fen):
        game_id = self.scope['url_route']['kwargs']['game_id']
        game_obj = Game.objects.get(id=game_id)
        game_obj.fen = new_fen
        game_obj.moves_list += ';' + new_fen
        game_obj.save()
        self.game_obj = game_obj

    def get_usernames(self):
        return self.game_obj.player_white.username, self.game_obj.player_black.username 

    async def timer_stop_broadcast(self, event):
        if self.timer_task is not None and self.timer_task != 'placeholder':
            asyncio.Task.cancel(self.timer_task)

    @database_sync_to_async
    def update_timer(self, timer, color):
        obj = self.game_obj
        if color == 'white':
            obj.timer_white = timer
        else:
            obj.timer_black = timer
        obj.save()

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

    def init_JSON(self):
        user = str(self.scope['user'])
        fen = self.game_obj.fen
        turn = self.game_obj.get_turn()
        color = self.game_obj.get_color(user)
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

    def vote_for_reset(self, player):
        self.game_obj.vote_for_reset(player)

    def check_for_reset(self):
        return self.game_obj.check_for_reset()

    @database_sync_to_async
    def reset_handler(self):
        username1 = self.game_obj.player_white.username
        username2 = self.game_obj.player_black.username
        game_id = self.game_obj.id
        Game.objects.get(id=game_id).delete()
        game_obj = get_game(username1, username2)
        game_obj.assign_colors_randomly(username1, username2)
        game_obj.is_running = True
        game_obj.save()
        return game_obj.id

    @database_sync_to_async
    def reset_JSON(self, new_game_id):
        game = Game.objects.get(id=new_game_id)
        fen = game.fen
        turn = game.get_turn()
        user = str(self.scope['user'])
        color = game.get_color(user)
        time_white = self.to_timer_format(game.timer_white)
        time_black = self.to_timer_format(game.timer_black)
        game_id = game.id
        data = {
            'type': 'reset',
            'fen': fen,
            'turn': turn,
            'time_black': time_black,
            'time_white': time_white,
            'game_id': game_id,
            'color': color
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
        game_id = self.scope['url_route']['kwargs']['game_id']
        game_obj = await self.get_game_by_id(game_id)
        game_obj.is_running = False
        game_obj.is_finished = True
        if game_result == 'whitewins':
            game_obj.winner = game_obj.player_white
        elif game_result == 'blackwins':
            game_obj.winner = game_obj.player_black
        elif game_result == 'stalemate':
            pass
        await database_sync_to_async(game_obj.save)()
        self.game_obj = game_obj
        return

    def promotion_handler(self, p, t, piece, turn):
        self.game_obj.promotion_handler(p, t, piece, turn)

    @database_sync_to_async
    def get_game_by_usernames(self, username1, username2):
        return Game.objects.get_or_new(username1, username2)


class InviteConsumer(AsyncJsonWebsocketConsumer):
    groups = ['invite_group']
    async def connect(self):
        await self.accept()

    async def receive_json(self, content):
        await self.channel_layer.group_send(
            'invite_group',
            {
                'type': 'invite_broadcast',
                'text': content
            }
        )

    async def disconnect(self, close_code):
        print('close_code:',close_code)

    async def invite_broadcast(self, content):
        msg = content['text']
        await self.send_json(msg)
           
