import os
import pickle
from pathlib import Path

from async_getters import get_puzzle_by_id, get_user_with_jwt
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from game.websocket import MyAsyncJsonWebsocketConsumer
from django_chess.settings import BASE_DIR
from game.game_engine.game_cls import Color, GameResult
from game.game_engine.game_funcs import number_to_field, opposite_color
from game.game_engine.stockfish import stockfish
from game.models import GameInProgress, Game

from .game_engine.game_engine import GameEngine
from .tasks import cancel_countdown_task, trigger_countdown_task, trigger_timer_task
from .misc import start_game, start_game_as_async
from asgiref.sync import sync_to_async

User = get_user_model()
channel_layer = get_channel_layer()


class GameConsumer(MyAsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope["cookies"]["jwt"]
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]

        self.user = await get_user_with_jwt(token)
        self.game_db_obj = await self.get_game_in_progress_obj(self.game_id)
        self.group_name = self.game_db_obj.group_name

        file_path_str = os.path.join(
            BASE_DIR, f"game/game_pickles/{self.game_db_obj.file_name}.pickle"
        )

        self.file_path = Path(file_path_str)
        with self.file_path.open("rb") as file:
            self.game_engine = pickle.load(file)
        await self.accept()

        cancel_countdown_task(self.game_engine.task_name, self.user.username)

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        data = self.game_engine.get_init_msg()

        await self.send_json(data)

    @database_sync_to_async
    def get_game_in_progress_obj(self, id):
        return GameInProgress.objects.get(id=id)

    async def receive_json(self, msg):
        with self.file_path.open("rb") as file:
            self.game_engine = pickle.load(file)

        type = msg["type"]

        if type == "move":
            await self.handle_move(msg)

        elif type == "promotion":
            await self.handle_promotion(msg)

        elif type == "draw":
            await self.handle_draw(msg)

        elif type == "move_cancel":
            await self.handle_move_cancel(msg)

        elif type == "resign":
            await self.handle_resign()

        elif type == "rematch":
            await self.handle_rematch(msg)

    async def handle_move(self, msg):
        pick_id = int(msg["pick_id"])
        drop_id = int(msg["drop_id"])
        move_result = self.game_engine.make_move(pick_id, drop_id)
        if move_result is not None:
            await self.process_move_result(move_result)

    async def handle_promotion(self, msg):
        piece_type = msg["piece_type"]
        move_result = self.game_engine.promotion_handler(piece_type)
        await self.process_promotion_move_result(move_result)

    @database_sync_to_async
    def save_game_to_db(self):
        data = self.game_engine.get_model_data()
        Game.objects.create_game(data)

    async def process_move_result(self, move_result):
        type = move_result["type"]
        if type == "promoting":
            await self.send_json({"type": type})
        elif type == "move":
            await self.group_broadcast(move_result)
        elif type == "game_end":
            await self.save_game_to_db()
            await self.group_broadcast(move_result)

    async def process_promotion_move_result(self, move_result):
        type = move_result["type"]
        if type == "move":
            await self.group_broadcast(move_result)
        elif type == "game_end":
            await self.save_game_to_db()
            await self.group_broadcast(move_result)

    async def handle_draw(self, msg):
        action = msg["action"]
        if action == "offer":
            await self.send_draw_offer()

        elif action == "accept":
            await self.accept_draw()

        elif action == "reject":
            await self.reject_draw_offer()

    async def send_draw_offer(self):
        msg = {"type": "draw_offer", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

    async def accept_draw(self):
        await self.end_game_with_result(GameResult.DRAW_AGREEMENT)

    async def reject_draw_offer(self):
        msg = {"type": "draw_reject", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

    async def handle_move_cancel(self, msg):
        action = msg["action"]
        if action == "request":
            try:
                await self.send_move_cancel_request()
            except IndexError:
                await self.send_json({"type": "move_cancel_error"})

        elif action == "accept":
            await self.accept_move_cancel_request()
            trigger_timer_task(self.game_engine)

        elif action == "reject":
            await self.reject_move_cancel_request(self.game_engine)

    async def send_move_cancel_request(self):
        sender_color = self.game_engine.get_user_color(self.user.username)
        game_positions = self.game_engine.game_positions

        try:
            if sender_color == self.game_engine.current_turn:
                fen = game_positions[-3]
            else:
                fen = game_positions[-2]
        except IndexError:
            raise

        msg = {"type": "move_cancel_request", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

        self.game_engine.move_cancel_fen = fen
        self.game_engine.save_game_pickle()

    async def reject_move_cancel_request(self):
        msg = {"type": "move_cancel_request", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

    async def accept_move_cancel_request(self):
        self.game_engine.move_cancel_handler()

        msg = self.game_engine.get_move_msg()
        await self.group_broadcast(msg)

    async def handle_resign(self):

        winner_color = opposite_color(
            self.game_engine.get_user_color(self.user.id)
        )
        if winner_color == Color.WHITE:
            game_result = GameResult.WHITEWINS_RESIGNED
        elif winner_color == Color.BLACK:
            game_result = GameResult.BLACKWINS_RESIGNED
        await self.end_game_with_result(game_result)

    async def end_game_with_result(self, game_result):
        self.game_engine.end_game(game_result)
        await self.save_game_to_db()
        msg = self.game_engine.get_game_end_msg()
        await self.group_broadcast(msg)

    async def group_broadcast(self, msg):
        await channel_layer.group_send(
            self.group_name, {"type": "basic_broadcast", "text": msg}
        )

    async def opponent_broadcast(self, msg):
        await channel_layer.group_send(
            self.group_name, {"type": "one_way_broadcast", "text": msg}
        )

    async def handle_rematch(self, msg):
        action = msg["action"]
        if action == "offer":
            await self.send_rematch()

        elif action == "accept":
            await self.accept_rematch()

        elif action == "reject":
            await self.reject_rematch()

    async def send_rematch(self):
        msg = {"type": "rematch", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

    async def accept_rematch(self):
        game_info = self.game_engine.game_info
        players = game_info['players']
        game_db_obj = await start_game_as_async(game_info)
    
        data = {
            'type': 'rematch_accept',
            'game_id': game_db_obj.id
        }
            
        await self.group_broadcast(data)
        
    async def reject_rematch(self):
        msg = {"type": "rematch_reject", "sender_channel_name": self.channel_name}
        await self.opponent_broadcast(msg)

    async def disconnect(self, close_code):
        if close_code == 1001 or close_code is None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            # check if no need to re-get the game
            if not self.game_engine.is_running:
                trigger_countdown_task(self.game_engine, self.user.id)
        # print('game_close_code:', close_code)

    async def basic_broadcast(self, data):
        msg = data["text"]
        await self.send_json(msg)

    async def one_way_broadcast(self, data):
        msg = data['text']
        if not self.channel_name == msg['sender_channel_name']:
            await self.send_json(msg)


class GameChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        ...

    async def receive_json(self, msg):
        ...

    async def disconnect(self, close_code):
        pass
        # print('game_chat_close_code:', close_code)

    async def basic_broadcast(self, msg):
        msg = msg["text"]
        await self.send_json(msg)


class StockfishConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, msg):
        type = msg["type"]

        if type == "position":
            await self.handle_position(msg)

    async def handle_position(self, msg):
        fen = msg["fen"]
        stockfish.set_fen_position(fen)
        evaluation = stockfish.get_evaluation()
        await self.send_json({"type": "stockfish_position", "eval": evaluation})

    async def disconnect(self, close_code):
        pass
        # print('stockfish_close_code:', close_code)


class GameFreeBoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        ...

    async def receive_json(self, msg):
        ...

    async def handle_move(self, msg):
        ...

    async def handle_promotion(self, msg):
        ...

    async def handle_reset(self):
        ...

    async def disconnect(self, close_code):
        ...
        # print('game_close_code:', close_code)


class GamePuzzleConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope["cookies"]["jwt"]
        self.user = await get_user_with_jwt(token)
        self.puzzle_id = self.scope["url_route"]["kwargs"]["puzzle_id"]
        self.puzzle_obj = await get_puzzle_by_id(self.puzzle_id)
        self.current_fen = self.puzzle_obj.fen

        data = {
            "type": "init",
            "fen": self.puzzle_obj.fen,
            "board_orientation": self.puzzle_obj.player_color,
        }

        await self.accept()
        await self.send_json(data)

    async def receive_json(self, msg):
        self.puzzle_id = self.scope["url_route"]["kwargs"]["puzzle_id"]
        self.puzzle_obj = await get_puzzle_by_id(self.puzzle_id)

        self.game_engine = GameEngine(fen=self.current_fen, is_puzzle=True)
        type = msg["type"]

        if type == "move":
            await self.handle_move(msg)

        elif type == "promotion":
            await self.handle_promotion(msg)

    async def handle_move(self, msg):
        pick_id = int(msg["pick_id"])
        drop_id = int(msg["drop_id"])
        move_result = self.game_engine.make_move(pick_id, drop_id)
        self.castles = move_result["castles"]
        if move_result["is_legal_flag"] is False:
            return
        elif move_result["game_result"] == "promoting":
            self.promotion_pick_id = pick_id
            self.promotion_drop_id = drop_id
            await self.send_json(
                {"type": "promoting", "turn": self.puzzle_obj.player_color}
            )
            return
        else:
            stockfish.set_fen_position(self.current_fen)
            best_move = stockfish.get_best_move()
            player_move = (
                number_to_field(pick_id)
                + number_to_field(drop_id)
            )
            if best_move == player_move:
                stockfish.make_moves_from_current_position([player_move])
                stockfish.make_moves_from_current_position([stockfish.get_best_move()])
                new_fen = stockfish.get_fen_position()
                self.current_fen = new_fen
                data = {"type": "move", "fen": new_fen}
                await self.send_json(data)

    async def handle_promotion(self, msg):
        piece_type = msg["piece_type"]
        stockfish.set_fen_position(self.current_fen)
        best_move = stockfish.get_best_move()
        player_move = (
            number_to_field(self.promotion_pick_id)
            + number_to_field(self.promotion_drop_id)
            + piece_type[0]
        )
        if best_move == player_move:
            stockfish.make_moves_from_current_position([player_move])
            stockfish.make_moves_from_current_position([stockfish.get_best_move()])
            new_fen = stockfish.get_fen_position()
            self.current_fen = new_fen
            data = {"type": "move", "fen": new_fen}
            await self.send_json(data)

    async def disconnect(self, close_code):
        pass
