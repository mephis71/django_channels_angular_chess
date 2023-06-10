from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from stockfish import Stockfish

from .game_engine import GameEngine
from .game_functions import *
from utils.getters import get_freeboard_game_by_id, get_game_by_id
from .tasks import (cancel_countdown_task, cancel_timer_task,
                    trigger_countdown_task, trigger_timer_task)
from .utils import (endgame_freeboard_JSON, init_freeboard_JSON, init_JSON,
                    move_freeboard_JSON, opposite_color)
from utils.getters import get_user_with_jwt

User = get_user_model()

stockfish = Stockfish(path='/usr/games/stockfish')

class GameLiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope['cookies']['jwt']
        self.user = await get_user_with_jwt(token)

        await self.accept()

        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_game_by_id(self.game_id)
        self.game_room_name = self.game_obj.get_game_name()

        if self.game_obj.is_finished:
            msg = endgame_JSON(self.game_obj)
            await self.send_json(msg)
            await self.channel_layer.group_add(
                self.game_room_name,
                self.channel_name
            )
            return

        cancel_countdown_task(self.game_obj, self.user.username)

        await self.channel_layer.group_add(
            self.game_room_name,
            self.channel_name
        )

        data = init_JSON(self.game_obj)
        await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_game_by_id(self.game_id)

        self.game_engine = GameEngine(self.game_obj)
        type = msg['type']

        if type == 'move':
            await self.handle_move(msg)

        elif type == 'promotion':
            await self.handle_promotion(msg)

        elif type == 'draw':
            await self.handle_draw(msg)

        elif type == 'move_cancel':
            await self.handle_move_cancel(msg)

        elif type == 'resign':
            await self.handle_resign()

        elif type == 'rematch':
            await self.handle_rematch(msg)

    async def handle_move(self, msg):
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

    async def handle_promotion(self, msg):
        turn = self.game_obj.get_turn()
        piece_type = msg['piece_type']
        game_result, new_fen = self.game_engine.promotion_handler(self.promotion_pick_id, self.promotion_drop_id, piece_type, turn, self.castles)
        self.castles = None
        self.game_obj = await update_game(self.game_obj, new_fen)
        trigger_timer_task(self.game_obj)
        if game_result != False:
            await end_game(self.game_obj, game_result)    
        await end_move(self.game_obj)

    async def handle_draw(self, msg):
        action = msg['action']
        if action == 'offer':
            await send_draw_offer(self.game_obj, self.channel_name)

        elif action == 'accept':
            await end_game(self.game_obj, 'draw-mutual')

        elif action == 'reject':
            await reject_draw_offer(self.game_obj)

    async def handle_move_cancel(self, msg):
        action = msg['action']
        if action == 'request':
            try:
                await send_move_cancel_request(self.game_obj, self.channel_name, self.user.username)
            except IndexError:
                await self.send_json({'type':'move_cancel_error'})

        elif action == 'accept':
            self.game_obj = await accept_move_cancel_request(self.game_obj)
            cancel_timer_task(self.game_obj)
            trigger_timer_task(self.game_obj)

        elif action == 'reject':
                await reject_move_cancel_request(self.game_obj)  

    async def handle_resign(self):
        winner_color = opposite_color(self.game_obj.get_color(self.user.username))
        await end_game(self.game_obj, f'{winner_color}wins-resignment')

    async def handle_rematch(self, msg):
        action = msg['action']
        if action == 'offer':
            await send_rematch(self.game_obj, self.channel_name)

        elif action == 'accept':
            await accept_rematch(self.game_obj)

        elif action == 'reject':
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

        # print('game_close_code:', close_code)

    async def basic_broadcast(self, event):
        data = event['text']
        await self.send_json(data)

    async def one_way_broadcast(self, event):
        data = event['text']
        if data['sender_channel_name'] != self.channel_name:
            await self.send_json(data)

class GameChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope['cookies']['jwt']
        self.user = await get_user_with_jwt(token)

        await self.accept()

        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_game_by_id(self.game_id)
        self.game_room_name = self.game_obj.get_game_name()

        await self.channel_layer.group_add(
                f'{self.game_room_name}_chat',
                self.channel_name
            )

    async def receive_json(self, msg):
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
            await self.handle_position(msg)

    async def handle_position(self, msg):
        fen = msg['fen']
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
        self.user = await get_user_with_jwt(token)
        
        await self.accept()
        
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_freeboard_game_by_id(self.game_id)

        data = init_freeboard_JSON(self.game_obj)
        await self.send_json(data)

    async def receive_json(self, msg):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_obj = await get_freeboard_game_by_id(self.game_id)
        self.game_engine = GameEngine(self.game_obj)
        type = msg['type']

        if type == 'move':
            await self.handle_move(msg)

        elif type == 'promotion':
            await self.handle_promotion(msg)
        
        elif type == 'reset':
            await self.handle_reset()
            

    async def handle_move(self, msg):
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

    async def handle_promotion(self, msg):
        turn = self.game_obj.get_turn()
        piece_type = msg['piece_type']
        game_result, new_fen = self.game_engine.promotion_handler(self.promotion_pick_id, self.promotion_drop_id, piece_type, turn, self.castles)
        self.castles = None
        self.game_obj = await update_freeboard_game(self.game_obj, new_fen)
        if game_result != False:
            await end_freeboard_game(self.game_obj, game_result)
            data = endgame_freeboard_JSON(self.game_obj)
            await self.send_json(data)

        data = move_freeboard_JSON(self.game_obj)
        await self.send_json(data)
    
    async def handle_reset(self):
        self.game_obj.reset()
        await database_sync_to_async(self.game_obj.save)()
        data = init_freeboard_JSON(self.game_obj)
        await self.send_json(data)

    async def disconnect(self, close_code):
        await database_sync_to_async (self.game_obj.delete)()
        # await database_sync_to_async(print)(FreeBoardGame.objects.all())

        # print('game_close_code:', close_code)