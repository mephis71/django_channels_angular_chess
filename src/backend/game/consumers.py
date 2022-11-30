import asyncio
import datetime
from datetime import timezone
from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rich import print
import jwt
from .game_engine import GameEngine
from .models import Game
from .tasks import trigger_timer_task
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import exceptions


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(self.scope)
        token = self.scope['cookies']['jwt']
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        except:
            raise exceptions.AuthenticationFailed('Invalid authentication. Could not decode token.')
        try:
            user = await database_sync_to_async (User.objects.get)(pk=payload['id'])
            self.user = user
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No user matching this token was found.')

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
            game_positions = self.game_obj.get_game_positions()
            data = self.init_JSON()
            self.game_engine = GameEngine(fen, game_positions)

            await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await self.get_game_by_id(self.game_id)

        user = self.user
        fen = self.game_obj.fen
        game_positions = self.game_obj.get_game_positions()
        self.game_engine = GameEngine(fen, game_positions)
        type = msg['type']

        if type == 'move':
            color = self.game_obj.get_color(user.username)
            if color != self.game_obj.get_turn():
                # try:
                #     raise Exception("Color of the player does not match game's current turn")
                # finally:
                #     print(color, self.game_obj.get_turn())
                return

            p = int(msg['pick_id'])
            t = int(msg['drop_id'])
            is_legal_flag, game_result, new_fen = self.game_engine.is_legal(p, t)

            if is_legal_flag == False:
                return
            elif game_result == 'promoting':
                data = {
                    'type': 'promoting'
                }
                self.promotion_p = p
                self.promotion_t = t
                await self.send_json(data)
                return   
            else:
                await self.update_game(new_fen)

            if game_result != False:
                await self.endgame_wrapper(game_result)
                
            await self.move_wrapper()
            return

        if type == 'promotion':
            current_turn = self.game_obj.get_turn()
            piece_type = msg['piece_type']
            game_result, new_fen = self.game_engine.promotion_handler(self.promotion_p, self.promotion_t, piece_type, current_turn)
            await self.update_game(new_fen)
            if game_result != False:
                await self.endgame_wrapper(game_result)

            await self.move_wrapper()
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
                        'type': 'draw_reject',
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

    
    async def update_game(self, new_fen):
        game_obj = await self.get_game_by_id(self.game_id)
        user = self.user
        color = self.game_obj.get_color(user.username)

        if game_obj.is_running == False:
            game_obj.is_running = True
            now = datetime.datetime.now(tz=timezone.utc)
            game_obj.game_start_time = now
            game_obj.last_move_time = now
        else:
            now = datetime.datetime.now(tz=timezone.utc)
            time_dif = now - self.game_obj.last_move_time
            time_dif_seconds = int(time_dif.seconds)
            if color == 'white':
                game_obj.timer_white -= time_dif_seconds
            elif color == 'black':
                game_obj.timer_black -= time_dif_seconds
            else:
                try:
                    raise Exception('Undefined color')
                finally:
                    print('color:', color)

            game_obj.last_move_time = now

        game_obj.fen = new_fen
        game_obj.game_positions += ';' + new_fen
        game_obj.move_timestamps += f';{game_obj.timer_white}-{game_obj.timer_black}'

        await database_sync_to_async(game_obj.save)()
        self.game_obj = game_obj
        trigger_timer_task(self.game_obj)

    def get_usernames(self):
        return self.game_obj.player_white.username, self.game_obj.player_black.username 

    @database_sync_to_async
    def get_game_by_id(self, game_id):
        return Game.objects.select_related("player_white", "player_black").get(id=game_id)
    
    def move_JSON(self):
        fen = self.game_obj.fen
        current_turn = self.game_obj.get_turn()
        time_black = to_timer_format(self.game_obj.timer_black)
        time_white = to_timer_format(self.game_obj.timer_white)
        game_positions = self.game_obj.get_game_positions()
        data = {
            'type': 'move',
            'fen': fen,
            'current_turn': current_turn,
            'time_black': time_black,
            'time_white': time_white,
            'game_positions': game_positions
        }
        return data

    def endgame_JSON(self, game_result):
        fen = self.game_obj.fen
        current_turn = self.game_obj.get_turn()
        time_black = to_timer_format(self.game_obj.timer_black)
        time_white = to_timer_format(self.game_obj.timer_white)
        game_positions = self.game_obj.get_game_positions()
        data = {
            'type': 'endgame',
            'fen': fen,
            'current_turn': current_turn,
            'time_black': time_black,
            'time_white': time_white,
            'game_result': game_result,
            'game_positions': game_positions
        }
        return data

    def init_JSON(self):
        user = self.user
        fen = self.game_obj.fen
        current_turn = self.game_obj.get_turn()
        player_color = self.game_obj.get_color(user.username)
        time_black = to_timer_format(self.game_obj.timer_black)
        time_white = to_timer_format(self.game_obj.timer_white)
        game_positions = self.game_obj.get_game_positions()
        data = {
            'type': 'init',
            'fen': fen,
            'player_color': player_color,
            'current_turn': current_turn,
            'time_black': time_black,
            'time_white': time_white,
            'game_positions': game_positions
        }
        return data

    def opposite_color(self, color):
        if color == 'black':
            return 'white'
        else:
            return 'black'

    async def end_game(self, game_result):
        game_obj = await self.get_game_by_id(self.game_id)
        for task in asyncio.Task.all_tasks():
            if task.get_name() == self.game_room_name:
                task.cancel()
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
        await database_sync_to_async(game_obj.add_to_history)()
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

        data = self.endgame_JSON(game_result)
        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'basic_broadcast',
                'text': data
            }
        )
        return

    async def move_wrapper(self):
        data = self.move_JSON()
        await self.channel_layer.group_send(
            self.game_room_name,
            {
                'type': 'basic_broadcast',
                'text': data
            }
        )
        return

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
           


def to_timer_format(seconds):
        s = int(seconds)
        m = s//60
        s = s - m*60
        if m < 10:
            m = f'0{m}'
        if s < 10:
            s = f'0{s}'
        return f'{m}:{s}'