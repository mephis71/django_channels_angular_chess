import jwt
from stockfish import Stockfish
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import FreeBoardGame
from .game_engine import GameEngine
from .game_functions import *
from .getters import get_freeboard_game_by_id, get_game_by_id
from .tasks import (cancel_countdown_task, cancel_timer_task,
                    trigger_countdown_task, trigger_timer_task)
from .utils import endgame_freeboard_JSON, init_JSON, init_freeboard_JSON, move_freeboard_JSON, opposite_color, move_JSON

User = get_user_model()

stockfish = Stockfish(path='/usr/games/stockfish')

from rest_framework import exceptions


class GameLiveConsumer(AsyncJsonWebsocketConsumer):
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
            move_result = self.game_engine.is_legal(pick_id, drop_id)
            self.castles = move_result['castles'] 
            if move_result['is_legal_flag'] == False:
                return
            elif move_result['game_result'] == 'promoting':
                self.promotion_pick_id = pick_id
                self.promotion_drop_id = drop_id
                await self.send_json({'type':'promoting'})
                return   
            else:
                self.game_obj = await update_game(self.game_obj, move_result['new_fen'])
                trigger_timer_task(self.game_obj)
                if move_result['game_result'] != False:
                    await end_game(self.game_obj, move_result['game_result'])
                else:
                    await end_move(self.game_obj)

        elif type == 'promotion':
            turn = self.game_obj.get_turn()
            piece_type = msg['piece_type']
            game_result, new_fen = self.game_engine.promotion_handler(self.promotion_pick_id, self.promotion_drop_id, piece_type, turn, self.castles)
            self.castles = None
            self.game_obj = await update_game(self.game_obj, new_fen)
            trigger_timer_task(self.game_obj)
            if game_result != False:
                await end_game(self.game_obj, game_result)

            await end_move(self.game_obj)

        elif type == 'draw_offer':
            await send_draw_offer(self.game_obj, self.channel_name)

        elif type == 'draw_accept':
            await end_game(self.game_obj, 'draw-mutual')

        elif type == 'draw_reject':
            await reject_draw_offer(self.game_obj)

        elif type == 'move_cancel_request':
            try:
                await send_move_cancel_request(self.game_obj, self.channel_name, self.user.username)
            except IndexError:
                await self.send_json({'type':'move_cancel_error'})

        elif type == 'move_cancel_accept':
            self.game_obj = await accept_move_cancel_request(self.game_obj)
            cancel_timer_task(self.game_obj)
            trigger_timer_task(self.game_obj)

        elif type == 'move_cancel_reject':
            await reject_move_cancel_request(self.game_obj)

        elif type == 'resign':
            winner_color = opposite_color(self.game_obj.get_color(self.user.username))
            await end_game(self.game_obj, f'{winner_color}wins-resignment')

        elif type == 'rematch':
            await send_rematch(self.game_obj, self.channel_name)
            
        elif type == 'rematch_accept':
            await accept_rematch(self.game_obj)

        elif type == 'rematch_reject':
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

        elif close_code == 4000:
            # 4000 - disconnecting after client connects to a game which has finished before
            pass
        # print('game_close_code:', close_code)

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
        pass
        # print('invite_close_code:', close_code)

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
        pass
        # print('game_chat_close_code:', close_code)

    async def basic_broadcast(self, msg):
        msg = msg['text']
        await self.send_json(msg)

class StockfishConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, msg):
        type = msg['type']
        if type == 'position':
            fen = msg['value']
            stockfish.set_fen_position(fen)
            evaluation = stockfish.get_evaluation()
            best_move = stockfish.get_best_move()
            await self.send_json({
                'type': 'stockfish_position',
                'eval': evaluation
            })

    async def disconnect(self, close_code):
        pass
        # print('stockfish_close_code:', close_code)

class GameFreeBoardConsumer(AsyncJsonWebsocketConsumer):
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
            self.game_obj = await get_freeboard_game_by_id(self.game_id)

            await self.accept()

            data = init_freeboard_JSON(self.game_obj)
            self.game_engine = GameEngine(self.game_obj)

            await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_freeboard_game_by_id(self.game_id)
        self.game_engine = GameEngine(self.game_obj)
        type = msg['type']

        if type == 'move':
            # TODO: move it to handle_move()
            pick_id = int(msg['pick_id'])
            drop_id = int(msg['drop_id'])
            move_result = self.game_engine.is_legal(pick_id, drop_id)
            self.castles = move_result['castles']
            if move_result['is_legal_flag'] == False:
                return
            elif move_result['game_result'] == 'promoting':
                self.promotion_pick_id = pick_id
                self.promotion_drop_id = drop_id
                await self.send_json({
                    'type':'promoting',
                    'turn': self.game_obj.get_turn()
                    })
                return   
            else:
                self.game_obj = await update_freeboard_game(self.game_obj, move_result['new_fen'])
                if move_result['game_result'] != False:
                    await end_freeboard_game(self.game_obj, move_result['game_result'])
                    data = endgame_freeboard_JSON(self.game_obj)
                    await self.send_json(data)
                else:
                    data = move_freeboard_JSON(self.game_obj)
                    await self.send_json(data)

        elif type == 'promotion':
            # TODO: move it to handle_promotion()
            turn = self.game_obj.get_turn()
            piece_type = msg['piece_type']
            # TODO: pass castles in promotion handler
            game_result, new_fen = self.game_engine.promotion_handler(self.promotion_pick_id, self.promotion_drop_id, piece_type, turn, self.castles)
            self.castles = None
            self.game_obj = await update_freeboard_game(self.game_obj, new_fen)
            if game_result != False:
                await end_freeboard_game(self.game_obj, game_result)
                data = endgame_freeboard_JSON(self.game_obj)
                await self.send_json(data)

            data = move_freeboard_JSON(self.game_obj)
            await self.send_json(data)
        
        elif type == 'reset':
            self.game_obj.reset()
            await database_sync_to_async(self.game_obj.save)()
            data = init_freeboard_JSON(self.game_obj)
            await self.send_json(data)
            
    async def disconnect(self, close_code):
        await database_sync_to_async (self.game_obj.delete)()
        # await database_sync_to_async(print)(FreeBoardGame.objects.all())

        # print('game_close_code:', close_code)