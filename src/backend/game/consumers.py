import jwt
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from rich import print

from .game_engine import GameEngine
from .tasks import cancel_countdown_task, trigger_countdown_task, trigger_timer_task, cancel_timer_task
from .utils import init_JSON, opposite_color
from .getters import get_game_by_id
from .game_functions import *

User = get_user_model()
from rest_framework import exceptions


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
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
        else:
            self.game_id = self.scope['url_route']['kwargs']['game_id']
            self.game_obj = await get_game_by_id(self.game_id)
            self.game_room_name = self.game_obj.get_game_name()

            if self.game_obj.is_finished:
                await self.accept()
                msg = endgame_JSON(self.game_obj)
                await self.send_json(msg)
                await self.close(code=4000)
                return

            await self.accept()

            cancel_countdown_task(self.game_obj, user.username)

            await self.channel_layer.group_add(
                self.game_room_name,
                self.channel_name
            )

            data = init_JSON(self.game_obj)
            self.game_engine = GameEngine(self.game_obj)

            await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_game_by_id(self.game_id)

        self.game_engine = GameEngine(self.game_obj)
        type = msg['type']
        if type == 'move':
            color = self.game_obj.get_color(self.user.username)
            if color != self.game_obj.get_turn():
                return
            pick_id = int(msg['pick_id'])
            drop_id = int(msg['drop_id'])
            is_legal_flag, game_result, new_fen = self.game_engine.is_legal(pick_id, drop_id)
            if is_legal_flag == False:
                return
            elif game_result == 'promoting':
                self.promotion_pick_id = pick_id
                self.promotion_drop_id = drop_id
                await self.send_json({'type':'promoting'})
                return   
            else:
                self.game_obj = await update_game(self.game_obj, new_fen)
                trigger_timer_task(self.game_obj)
                if game_result != False:
                    await end_game(self.game_obj, game_result)
                else:
                    await end_move(self.game_obj)
            return

        if type == 'promotion':
            turn = self.game_obj.get_turn()
            piece_type = msg['piece_type']
            game_result, new_fen = self.game_engine.promotion_handler(self.promotion_pick_id, self.promotion_drop_id, piece_type, turn)
            self.game_obj = await update_game(self.game_obj, new_fen)
            trigger_timer_task(self.game_obj)
            if game_result != False:
                await end_game(self.game_obj, game_result)

            await end_move(self.game_obj)
            return

        if type == 'draw_offer':
            await send_draw_offer(self.game_obj, self.channel_name)
            return

        if type == 'draw_accept':
            await end_game(self.game_obj, 'draw-mutual')
            return

        if type == 'draw_reject':
            await reject_draw_offer(self.game_obj)
            return

        if type == 'move_cancel_request':
            try:
                await send_move_cancel_request(self.game_obj, self.channel_name, self.user.username)
            except IndexError:
                await self.send_json({'type':'move_cancel_error'})
            return

        if type == 'move_cancel_accept':
            self.game_obj = await accept_move_cancel_request(self.game_obj)
            cancel_timer_task(self.game_obj)
            trigger_timer_task(self.game_obj)
            return

        if type == 'move_cancel_reject':
            await reject_move_cancel_request(self.game_obj)
            return

        if type == 'resign':
            winner_color = opposite_color(self.game_obj.get_color(self.user.username))
            await end_game(self.game_obj, f'{winner_color}wins-resignment')

        if type == 'rematch':
            await send_rematch(self.game_obj, self.channel_name)
            
        if type == 'rematch_accept':
            await accept_rematch(self.game_obj)

        if type == 'rematch_reject':
            await reject_rematch(self.game_obj, self.channel_name)



    async def disconnect(self, close_code):
        if close_code == 1001 or close_code == None:
            await self.channel_layer.group_discard(
                self.game_room_name,
                self.channel_name
            )
            # re-getting the game (without it, trigger_countdown_task function runs even when the game is finished, because after the endgame
            # the consumers do not update the game_obj in the receive_json function(temporary, can be fixed by assigning the game in basic_broadcast()
            # in the end_game() function))
            self.game_obj = await get_game_by_id(self.game_id)
            if not self.game_obj.is_finished:
                trigger_countdown_task(self.game_obj, self.user.username)

        if close_code == 4000:
            # 4000 - disconnecting after client connects to a game which has finished before
            pass
        print('game_close_code:', close_code)

    async def basic_broadcast(self, event):
        data = event['text']
        await self.send_json(data)

    async def one_way_broadcast(self, event):
        data = event['text']
        if data['sender_channel_name'] != self.channel_name:
            await self.send_json(data)

class InviteConsumer(AsyncJsonWebsocketConsumer):
    groups = ['invite_group']
    async def connect(self):
        await self.accept()

    async def receive_json(self, msg):
        msg['sender_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            'invite_group',
            {
                'type': 'one_way_broadcast',
                'text': msg
            }
        )

    async def disconnect(self, close_code):
        print('invite_close_code:', close_code)

    async def one_way_broadcast(self, msg):
        msg = msg['text']
        if self.channel_name != msg['sender_channel_name']:
            await self.send_json(msg)

    async def basic_broadcast(self, msg):
        msg = msg['text']
        await self.send_json(msg)

class GameChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope['cookies']['jwt']
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        except:
            raise exceptions.AuthenticationFailed('Invalid authentication. Could not decode token.')
        try:
            user = await database_sync_to_async (User.objects.get)(pk=payload['id'])
            self.user = user
            self.username = self.user.username
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No user matching this token was found.')

        await self.accept()

        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_game_by_id(self.game_id)
        self.game_room_name = self.game_obj.get_game_name()

        await self.channel_layer.group_add(
                f'{self.game_room_name}_chat',
                self.channel_name
            )

    async def receive_json(self, msg):
        msg['username'] = self.username
        await self.channel_layer.group_send(
            f'{self.game_room_name}_chat',
            {
                'type': 'basic_broadcast',
                'text': msg
            }
        )

    async def disconnect(self, close_code):
        print('game_chat_close_code:', close_code)

    async def basic_broadcast(self, msg):
        msg = msg['text']
        await self.send_json(msg)
