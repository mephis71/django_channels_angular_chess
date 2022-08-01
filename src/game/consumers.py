import asyncio
import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Game
from rich import print

class GameConsumer(AsyncConsumer):

    async def websocket_connect(self, event):

        # accept the connection
        await self.send({
            'type': 'websocket.accept',
        })
        self.timer_task = None

        # grab user and the game object
        game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await self.get_game_by_id(game_id)
        me = self.scope['user']

        print(me, 'connected')

        # grab the name of the 'game room' and assign it to the class
        game_room_name = self.game_obj.get_game_name()
        self.game_room_name = game_room_name

        # add the player (consumer) to the 'game room' (game_room_name)
        await self.channel_layer.group_add(
            game_room_name,
            self.channel_name
        )

        # add the user to the list of connected players in model
        await self.add_player(me)

        # grab the game state
        fen = await self.get_fen()

        # data contains color of the player and fen of the game, turn and type of 'init'
        data = await self.init_JSON(fen, me)

        turn = await self.get_turn()
        player = await self.get_color(me)

        if turn != player:
            self.timer_task = 'placeholder'

        # send the state of the game to the player which then updates the game on his side
        await self.send({
            'type': 'websocket.send',
            'text': data
        })

    async def websocket_receive(self, event):

        # decode from JSON
        msg = event['text']
        msg = json.loads(msg)

        # check if the message is a 'move' or 'reset' type
        type = msg['type']

        if type == 'move':
            
            game_id = self.scope['url_route']['kwargs']['game_id']
            self.game_obj = await self.get_game_by_id(game_id)
            p = msg['picked_id']
            t = msg['target_id']

            is_legal_flag, game_result = await self.is_legal(p, t)

            if is_legal_flag == False:
                return
            
            # if the game ends
            if game_result != False:
                await self.channel_layer.group_send(
                    self.game_room_name,
                    {
                        'type': 'timer_stop_broadcast'
                    }
                )

                jsonObj = await self.endgame_JSON(game_result)

                await self.channel_layer.group_send(
                    self.game_room_name,
                    {
                        'type': 'basic_broadcast',
                        'text': jsonObj
                    }
                )
                return
                
            player = msg['player']
            player = self.opposite_color(player)

            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'timer_handler',
                    'text': player
                }
            )

            jsonObj = await self.move_JSON()

            # send the move (new state of the game) to the other player (actually to both [group of self.game_room_name] but that doesnt make a difference)
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'basic_broadcast',
                    'text': jsonObj
                }
            )
            return


        if type == 'reset':
            player = msg['player']
            await self.vote_for_reset(player)
            if await self.check_for_reset() == True:
                await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'timer_stop_broadcast'
                }
            )
                await self.reset_handler()
                jsonObj = await self.reset_JSON()
                await self.channel_layer.group_send(
                    self.game_room_name,
                    {
                        'type': 'basic_broadcast',
                        'text': jsonObj
                    }
                )
            return

    async def websocket_disconnect(self, event):

        # remove the user from the list of connected players in model
        me = self.scope['user']
        await self.remove_player(me)

        await self.save_game()

        # remove consumer from the group
        await self.channel_layer.group_discard(
            self.game_room_name,
            self.channel_name
        )

        # disconnect
        await self.send({
            'type': 'websocket.disconnect'
        })

    async def timer_handler(self, event):
        if self.timer_task is None:
            player = event['text']
            self.timer_task = asyncio.create_task(self.timer_countdown(player))
        elif self.timer_task == 'placeholder':
            self.timer_task = None
        else:
            asyncio.Task.cancel(self.timer_task)
            self.timer_task = None

    async def timer_countdown(self, player):
        timer = self.get_timer(player)
        timer_color = player

        while timer > 0:

            await asyncio.sleep(1)
            timer -= 1
            await self.update_timer(timer, timer_color)
            timer_formatted = self.to_timer_format(timer)

            data = {
                'type': 'time',
                'time': timer_formatted,
                'timer_color': timer_color
            }

            jsonObj = json.dumps(data)

            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'basic_broadcast',
                    'text': jsonObj
                }
            )

    def get_timer(self, color):
        if color == 'white':
            timer = self.game_obj.timer_white
        else:
            timer = self.game_obj.timer_black
        return timer

    # handler for sending the position of the game to both players using group
    async def basic_broadcast(self, event):
        jsonObj = event['text']

        await self.send({
            "type": 'websocket.send',
            'text': jsonObj
        })

    async def timer_stop_broadcast(self, event):
        if self.timer_task is not None and self.timer_task != 'placeholder':
            asyncio.Task.cancel(self.timer_task)

    @database_sync_to_async
    def save_game(self):
        self.game_obj.save()

    @database_sync_to_async
    def update_timer(self, timer, color):
        obj = self.game_obj
        if color == 'white':
            obj.timer_white = timer
        else:
            obj.timer_black = timer
        obj.save()

    @database_sync_to_async
    def get_game_by_users(self, username1, username2):
        return Game.objects.get_or_new(username1, username2)

    @database_sync_to_async
    def get_game_by_id(self, game_id):
        return Game.objects.get(id=game_id)

    @database_sync_to_async
    def get_fen(self):
        return self.game_obj.fen

    @database_sync_to_async
    def get_turn(self):
        return self.game_obj.turn

    @database_sync_to_async
    def get_color(self, player):
        return self.game_obj.get_color(player)

    @database_sync_to_async
    def add_player(self, username):
        self.game_obj.add_player(username)

    @database_sync_to_async
    def remove_player(self, username):
        self.game_obj.remove_player(username)

    @database_sync_to_async
    def move_JSON(self):
        fen = self.game_obj.fen
        turn = self.game_obj.turn
        data = {
            'type': 'move',
            'fen': fen,
            'turn': turn
        }
        jsonObj = json.dumps(data)
        
        return jsonObj

    @database_sync_to_async
    def endgame_JSON(self, game_result):
        fen = self.game_obj.fen
        turn = self.game_obj.turn
        data = {
            'type': 'endgame',
            'fen': fen,
            'turn': turn,
            'game_result': game_result
        }
        jsonObj = json.dumps(data)
        
        return jsonObj

    @database_sync_to_async
    def init_JSON(self, fen, user):
        turn = self.game_obj.turn
        color = self.game_obj.get_color(user)
        time_black = self.to_timer_format(self.game_obj.timer_black)
        time_white = self.to_timer_format(self.game_obj.timer_white)
        jsonObj = {
            'type': 'init',
            'fen': fen,
            'color': color,
            'turn': turn,
            'time_black': time_black,
            'time_white': time_white
        }

        jsonObj = json.dumps(jsonObj)
        return jsonObj

    @database_sync_to_async
    def vote_for_reset(self, player):
        self.game_obj.vote_for_reset(player)

    @database_sync_to_async
    def check_for_reset(self):
        return self.game_obj.check_for_reset()

    @database_sync_to_async
    def reset_handler(self):
        game = self.game_obj
        game.fen = Game.DEFAULT_GAME_FEN
        game.turn = Game.STARTING_PLAYER
        game.timer_black = Game.DEFAULT_SECONDS
        game.timer_white = Game.DEFAULT_SECONDS
        game.reset_votes['white'] = False
        game.reset_votes['black'] = False
        game.save()

    @database_sync_to_async
    def reset_JSON(self):
        game = self.game_obj
        fen = game.fen
        turn = game.turn
        time_white = self.to_timer_format(game.timer_white)
        time_black = self.to_timer_format(game.timer_black)

        jsonObj = {
            'type': 'reset',
            'fen': fen,
            'turn': turn,
            'time_black': time_black,
            'time_white': time_white
        }

        jsonObj = json.dumps(jsonObj)

        return jsonObj

    @database_sync_to_async
    def is_legal(self, p , t):
        game = self.game_obj
        output = game.is_legal(p, t)
        return output

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

class InviteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({
            'type': 'websocket.accept'
        })

        await self.channel_layer.group_add(
            'invite_group',
            self.channel_name
        )

    async def websocket_receive(self, event):
        msg = json.loads(event['text'])
        await self.channel_layer.group_send(
            'invite_group',
            {
                'type': 'invite_broadcast',
                'text': msg
            }
        )
    
    async def websocket_disconnect(self, event):

        await self.channel_layer.group_discard(
            'invite_group',
            self.channel_name
        )

        await self.send({
            'type': 'websocket.disconnect'
        })


    async def invite_broadcast(self, event):
        msg = event['text']
        msg = json.dumps(msg)
   
        await self.send({
            'type': 'websocket.send',
            'text': msg
        })

