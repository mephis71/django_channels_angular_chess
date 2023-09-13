import datetime
import os
import pickle
import re
import uuid
from dataclasses import dataclass, field
from datetime import timezone
from pathlib import Path

from django_chess.settings import BASE_DIR
from game.game_engine.game_cls import FEN, Color, GameResult, Piece, PieceType
from game.game_engine.game_funcs import (
    field_to_number,
    number_to_field,
    opposite_color,
    piece_str_to_fen_letter,
    to_seconds,
    to_timestamp,
)
from game.game_engine.game_vars import DEFAULT_GAME_FEN
from dataclasses import fields, MISSING

@dataclass
class GameEngine:
    # Init values.
    players: dict
    duration: int
    init_fen: str = DEFAULT_GAME_FEN
    random_colors: bool = False

    # Players info.
    winner_id: int | None = field(init=False)

    # FEN
    fen: FEN = field(init=False)

    # En passant variables.
    prev_pick_id: int = field(init=False)
    prev_drop_id: int = field(init=False)

    # Promotion variables.
    promotion_pick_id: int = field(init=False)
    promotion_drop_id: int = field(init=False)

    # Game info.
    is_running: bool = field(init=False)
    timer_black: int = field(init=False)
    timer_white: int = field(init=False)
    game_positions: list[str] = field(init=False)
    move_timestamps: list[(int, int)] = field(init=False)
    move_history: list[(int, int)] = field(init=False)
    game_result: GameResult = field(init=False)

    # Game timing.
    start_time: str = field(init=False)
    last_move_time: str = field(init=False)
    end_time: str = field(init=False)

    # Engine variables.
    pieces: list[None | Piece] = field(init=False)
    possible_moves: list[bool] = field(init=False)
    attacked_fields: list[bool] = field(init=False)

    # Channels, pickles variables.
    uuid: str = field(init=False)

    # Move cancel variables
    move_cancel_fen: str = field(init=False)

    @classmethod
    def check_for_unassigned_fields(cls):
        # TODO: test
        datacls_fields = fields(cls)
        for field in datacls_fields:
            if field.default is not MISSING:
                AttributeError(f'{field.name} is unassigned.')

    @property
    def file_name(self) -> str:
        return f"game_{self.uuid}"

    @property
    def task_name(self) -> str:
        return f"task_{self.uuid}"

    @property
    def group_name(self) -> str:
        return f"group_{self.uuid}"

    @property
    def timers(self) -> tuple[str, ...]:
        timers = (self.timer_white, self.timer_black)
        return to_timestamp(timers)

    @property
    def current_turn(self) -> Color:
        """Returns color of the player whose turn it is."""
        return self.fen.turn_color
    
    @property
    def game_info(self):
        players_list = [self.players[key] for key in self.players]
        if self.random_colors:
            white_id = self.players['white']
            black_id = self.players['black']
        else:
            white_id = None
            black_id = None
        return {
            'players': players_list,
            'settings': {
                'white_id': white_id,
                'black_id': black_id,
                'random_colors': self.random_colors,
                'duration': self.duration,
            }
        }
        
    @property
    def players_list(self):
        return [self.players[key] for key in self.players.keys()]

    def get_user_color(self, user_id: int) -> Color:
        """Returns color of the player by username."""
        if self.players["white"] == user_id:
            return Color.WHITE
        elif self.players["black"] == user_id:
            return Color.BLACK

    def get_move_timestamps_str(self) -> str:
        """Returns a str of move timestamps to be saved to database."""
        move_timestamps = [
            "-".join(map(str, timestamp)) for timestamp in self.move_timestamps
        ]
        return ";".join(move_timestamps)

    def get_game_positions_str(self) -> str:
        """Returns a str of game positions to be saved to database."""
        return ";".join(self.game_positions)

    def get_move_history_str(self) -> str:
        """Returns a str of move history to be saved to database."""
        move_history = ["-".join(map(str, move)) for move in self.move_history]
        return ";".join(move_history)

    def __post_init__(self) -> None:
        """Game set-up after creating class object."""
        self.set_game_variables()
        self.set_en_passant_vars()
        self.set_pieces()

        self.set_uuid()
        self.init_file_path()
        self.check_for_unassigned_fields()

    def reset(self) -> None:
        """Not tested."""
        self.set_game_variables()
        self.set_en_passant_vars()
        self.set_pieces()

    def set_uuid(self) -> None:
        self.uuid = uuid.uuid4()

    def save_game_pickle(self) -> None:
        """Saves the current state of the class to the file. Invoked during end_move(), end_game(), and move_cancel_handler()."""
        with self.file_path.open("wb") as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def init_file_path(self) -> None:
        self.file_path_str = os.path.join(
            BASE_DIR, f"game/game_pickles/{self.file_name}.pickle"
        )
        self.file_path = Path(self.file_path_str)

    def set_file_path(self, file_path: str) -> None:
        self.file_path_str = file_path
        self.file_path = Path(file_path)

    def set_pieces(self) -> None:
        """Sets self.pieces with current FEN."""
        fen_pieces = self.fen.pieces
        fen_castles = self.fen.castles
        position = 0
        for letter in fen_pieces:
            if letter == "/":
                continue
            if re.match("[0-9]", letter):
                position += int(letter)
                continue
            if letter == "p":
                self.pieces[position] = Piece(Color.BLACK, PieceType.PAWN)
            if letter == "n":
                self.pieces[position] = Piece(Color.BLACK, PieceType.KNIGHT)
            if letter == "b":
                self.pieces[position] = Piece(Color.BLACK, PieceType.BISHOP)
            if letter == "r":
                self.pieces[position] = Piece(Color.BLACK, PieceType.ROOK)
            if letter == "q":
                self.pieces[position] = Piece(Color.BLACK, PieceType.QUEEN)
            if letter == "k":
                self.pieces[position] = Piece(Color.BLACK, PieceType.KING)
            if letter == "P":
                self.pieces[position] = Piece(Color.WHITE, PieceType.PAWN)
            if letter == "N":
                self.pieces[position] = Piece(Color.WHITE, PieceType.KNIGHT)
            if letter == "B":
                self.pieces[position] = Piece(Color.WHITE, PieceType.BISHOP)
            if letter == "R":
                self.pieces[position] = Piece(Color.WHITE, PieceType.ROOK)
            if letter == "Q":
                self.pieces[position] = Piece(Color.WHITE, PieceType.QUEEN)
            if letter == "K":
                self.pieces[position] = Piece(Color.WHITE, PieceType.KING)
            position += 1
        if fen_castles != "-":
            for letter in fen_castles:
                if letter == "K":
                    self.pieces[60] = Piece(Color.WHITE, PieceType.KING)
                    self.pieces[63] = Piece(Color.WHITE, PieceType.ROOK)
                if letter == "Q":
                    self.pieces[60] = Piece(Color.WHITE, PieceType.KING)
                    self.pieces[56] = Piece(Color.WHITE, PieceType.ROOK)
                if letter == "q":
                    self.pieces[4] = Piece(Color.BLACK, PieceType.KING)
                    self.pieces[0] = Piece(Color.BLACK, PieceType.ROOK)
                if letter == "k":
                    self.pieces[4] = Piece(Color.BLACK, PieceType.KING)
                    self.pieces[7] = Piece(Color.BLACK, PieceType.ROOK)

    def set_en_passant_vars(self) -> None:
        """Sets en passant variables with current FEN."""
        if self.fen.enpassant != "-":
            trgt = field_to_number(self.fen.enpassant)
            if self.fen.turn == "w":
                self.prev_pick_id = trgt - 8
                self.prev_drop_id = trgt + 8
            if self.fen.turn == "b":
                self.prev_pick_id = trgt + 8
                self.prev_drop_id = trgt - 8

    def set_game_variables(self) -> None:
        """Sets the initial state of game variables."""
        self.fen = FEN(self.init_fen)
        self.set_both_timers(self.duration)
        self.pieces = [None] * 64
        self.possible_moves = [False] * 64
        self.attacked_fields = [False] * 64
        self.prev_pick_id = None
        self.prev_drop_id = None
        self.promotion_pick_id = None
        self.promotion_drop_id = None
        self.is_running = False
        self.game_positions = [self.fen.fen]
        self.move_timestamps = [self.timers]
        self.move_history = []
        self.winner_id = None
        self.move_cancel_fen = None

    def set_both_timers(self, duration) -> None:
        """Sets timers to a given duration (in seconds)."""
        self.timer_white = duration * 60
        self.timer_black = duration * 60

    def make_move(self, pick_id, drop_id) -> (dict[str, any] | None):
        """
        Moves a piece from pieces[pick_id] to pieces[drop_id].
        Returns move result or None if the move is not made.
        Possible move results are of types: 'promoting', 'move', 'game_end'.
        This function returns the output of end_move() or get_promoting_msg() functions or simply None.
        """
        pick_id = int(pick_id)
        drop_id = int(drop_id)
        if not self.is_correct_piece(pick_id):
            return None
        if self.is_move_enpassant(pick_id, drop_id):
            return self.enpassant_handler(pick_id, drop_id)
        if self.is_move_castles(pick_id, drop_id):
            return self.castles_handler(pick_id, drop_id)
        if not self.is_move_legal(pick_id, drop_id):
            return None

        self.update_halfmoves(pick_id, drop_id)
        self.update_castles_to_pop(pick_id, drop_id)

        self.move_piece(pick_id, drop_id)

        if self.is_pawn_promotion(drop_id):
            self.save_promotion_pick(pick_id, drop_id)
            return self.get_promoting_msg()

        self.update_enpassant_sqr(pick_id, drop_id)

        return self.end_move(pick_id, drop_id)

    def save_promotion_pick(self, pick_id, drop_id) -> None:
        """Saves pick and drop id of a promotion move to be used later in promotion_handler()."""
        self.promotion_pick_id = pick_id
        self.promotion_drop_id = drop_id

    def update_castles_to_pop(self, pick_id, drop_id) -> None:
        """Updates the _castles_to_pop variables of the self.fen object."""
        self.update_castles_to_pop_rook(pick_id, drop_id)
        self.update_castles_to_pop_king(pick_id)

    def update_castles_to_pop_king(self, pick_id) -> None:
        """Updates the FEN letters which are to be removed from game's FEN."""
        moving_piece = self.pieces[pick_id]
        if moving_piece.type == PieceType.KING:
            if moving_piece.color == Color.WHITE:
                self.fen._castles_to_pop += "QK"
            elif moving_piece.color == Color.BLACK:
                self.fen._castles_to_pop += "qk"

    def update_enpassant_sqr(self, pick_id, drop_id) -> None:
        """Updates the en passant square if a pawn made a two-field move, if not sets it to '-'."""
        if abs(drop_id - pick_id) == 16 and self.pieces[drop_id].type == PieceType.PAWN:
            if self.current_turn == Color.WHITE:
                self.fen._enpassant = number_to_field(drop_id + 8)
            elif self.current_turn == Color.BLACK:
                self.fen._enpassant = number_to_field(drop_id - 8)
        else:
            self.fen._enpassant = "-"

    def is_pawn_promotion(self, drop_id) -> bool:
        """Checks if the move leads to a pawn promotion."""
        is_pawn = self.pieces[drop_id].type == PieceType.PAWN
        is_last_square_reached = (
            drop_id < 8 if self.current_turn == Color.WHITE else drop_id >= 56
        )
        return is_pawn and is_last_square_reached

    def move_piece(self, pick_id, drop_id) -> None:
        """Moves a piece from self.pieces[pick_id] to self.pieces[drop_id] and leaves self.pieces[pick_id] empty."""
        moving_piece = self.pieces[pick_id]
        self.pieces[pick_id] = None
        self.pieces[drop_id] = Piece(moving_piece.color, moving_piece.type)

    def is_correct_piece(self, pick_id) -> bool:
        """Checks if a player selected a valid piece."""
        not_empty = not self.is_field_empty(pick_id)
        correct_color = not self.is_wrong_piece_color(pick_id)
        return not_empty and correct_color

    def is_move_enpassant(self, pick_id, drop_id) -> bool:
        """Checks if the attempted move is an en passant."""
        is_previous_move = self.prev_drop_id is not None and self.prev_pick_id is not None
        if is_previous_move:
            is_previous_move_pawn = self.pieces[self.prev_drop_id] is not None and self.pieces[self.prev_drop_id].type == PieceType.PAWN
            is_previous_move_double = abs(self.prev_pick_id - self.prev_drop_id) == 16
            is_pawn_move = self.pieces[pick_id].type == PieceType.PAWN
            is_in_enpassant_pos = abs(pick_id - self.prev_drop_id) == 1
            is_move_to_enpassant_sqr = abs(self.prev_drop_id - drop_id) == 8
        return is_previous_move and is_previous_move_pawn and is_previous_move_double and is_pawn_move and is_in_enpassant_pos and is_move_to_enpassant_sqr

    def enpassant_handler(self, pick_id, drop_id) -> (dict[str, any] | None):
        """Handles the en passant mechanics, returns True if the move was made, False otherwise."""
        origin_pieces = self.pieces.copy()
        origin_attacked_fields = self.attacked_fields.copy()

        self.update_castles_to_pop(pick_id, drop_id)

        moving_pawn = self.pieces[pick_id]
        self.pieces[drop_id] = Piece(moving_pawn.color, moving_pawn.type)
        self.pieces[pick_id] = None
        self.pieces[self.prev_drop_id] = None

        if self.is_checked():
            self.pieces = origin_pieces
            self.attacked_fields = origin_attacked_fields
            self.fen._castles_to_pop = ""
            return None
        else:
            self.fen._enpassant = "-"
            self.fen._halfmoves = 0

            return self.end_move(pick_id, drop_id)

    def is_move_castles(self, pick_id, drop_id) -> bool:
        """Checks if the attempted move is castling."""
        is_king_move = self.pieces[pick_id].type == PieceType.KING
        is_move_double = abs(drop_id - pick_id) == 2
        return is_king_move and is_move_double

    def castles_handler(self, pick_id, drop_id) -> (dict[str, any] | None):
        """Handles the castles mechanics, returns True if the move was made, False otherwise."""
        # save the pieces position so it can be restored later in case the player is being checked after castles (rare)
        origin_pieces = self.pieces.copy()
        origin_attacked_fields = self.attacked_fields.copy()

        self.update_castles_to_pop(pick_id, drop_id)

        moving_piece = self.pieces[pick_id]
        self.pieces[pick_id] = None
        if drop_id == 2:
            self.pieces[drop_id] = Piece(moving_piece.color, PieceType.KING)
            self.pieces[0] = None
            self.pieces[3] = Piece(moving_piece.color, PieceType.ROOK)
        elif drop_id == 6:
            self.pieces[drop_id] = Piece(moving_piece.color, PieceType.KING)
            self.pieces[7] = None
            self.pieces[5] = Piece(moving_piece.color, PieceType.ROOK)
        elif drop_id == 58:
            self.pieces[drop_id] = Piece(moving_piece.color, PieceType.KING)
            self.pieces[56] = None
            self.pieces[59] = Piece(moving_piece.color, PieceType.ROOK)
        elif drop_id == 62:
            self.pieces[drop_id] = Piece(moving_piece.color, PieceType.KING)
            self.pieces[63] = None
            self.pieces[61] = Piece(moving_piece.color, PieceType.ROOK)

        # if the player is checked after castles return False
        if self.is_checked():
            self.pieces = origin_pieces
            self.attacked_fields = origin_attacked_fields
            self.fen._castles_to_pop = ""
            return None
        else:
            self.fen._enpassant = "-"
            self.fen._halfmoves = self.fen.halfmoves + 1

            if self.current_turn == Color.WHITE:
                self.fen._castles_to_pop += "QK"
            elif self.current_turn == Color.BLACK:
                self.fen._castles_to_pop += "qk"

            return self.end_move(pick_id, drop_id)

    def is_move_legal(self, pick_id, drop_id) -> bool:
        """Checks if the move is legal."""
        self.update_possible_moves(pick_id)

        is_legal = not (self.is_move_against_pattern(drop_id) or self.is_checked_nextmove(pick_id, drop_id))
        return is_legal

    def update_halfmoves(self, pick_id, drop_id) -> None:
        """
        Reset halfmoves if there is a capture or
        pawn has been moved, else increment it.
        """
        is_capture = self.pieces[drop_id] is not None
        is_pawn_move = self.pieces[pick_id].type == PieceType.PAWN
        if is_capture or is_pawn_move:
            self.fen._halfmoves = 0
        else:
            self.fen._halfmoves = self.fen.halfmoves + 1

    def update_castles_to_pop_rook(self, pick_id, drop_id) -> None:
        """Updates FEN castles letters to pop from the game's fen."""
        castles_to_pop = ""
        is_rook_captured = self.pieces[drop_id] is not None and self.pieces[drop_id].type == PieceType.ROOK
        if is_rook_captured:
            if drop_id == 0:
                castles_to_pop += "q"
            elif drop_id == 7:
                castles_to_pop += "k"
            elif drop_id == 56:
                castles_to_pop += "Q"
            elif drop_id == 63:
                castles_to_pop += "K"

        moving_piece = self.pieces[pick_id]
        if moving_piece.type == PieceType.ROOK:
            if moving_piece.color == Color.BLACK:
                if pick_id == 0:
                    castles_to_pop += "q"
                elif pick_id == 7:
                    castles_to_pop += "k"
            elif moving_piece.color == Color.WHITE:
                if pick_id == 56:
                    castles_to_pop += "Q"
                elif pick_id == 63:
                    castles_to_pop += "K"

        self.fen._castles_to_pop += castles_to_pop

    def is_field_empty(self, pick_id) -> bool:
        """Checks if the picked field is empty."""
        return self.pieces[pick_id] is None

    def is_wrong_piece_color(self, pick_id) -> bool:
        """Checks if the picked piece is not of the player's color."""
        return self.pieces[pick_id].color != self.current_turn

    def is_move_against_pattern(self, drop_id) -> bool:
        """Checks if the attempted move is against the moving pattern of the piece."""
        return not self.possible_moves[drop_id]

    def is_checked_nextmove(self, pick_id, drop_id) -> bool:
        """Checks if the attempted move results in the moving player being checked."""

        # saving 'attacked_fields' list so it can be restored later because it's going to get changed in is_checked() function
        # same with 'self.pieces'

        origin_pieces = self.pieces.copy()
        origin_attacked_fields = self.attacked_fields.copy()

        moving_piece = self.pieces[pick_id]

        self.pieces[drop_id] = moving_piece
        self.pieces[pick_id] = None

        is_checked = self.is_checked()

        self.pieces = origin_pieces
        self.attacked_fields = origin_attacked_fields

        return is_checked

    def is_checked(self) -> bool:
        self.update_attacked_fields()
        type_list = [
            piece.type if piece is not None and piece.color is self.current_turn else None
            for piece in self.pieces
        ]
        king_position = type_list.index(PieceType.KING)
        return self.attacked_fields[king_position]

    def update_fen(self) -> None:
        fen_pieces = ""
        empty_spaces = 0

        for i in range(64):
            if self.pieces[i] is None:
                empty_spaces += 1
            else:
                if empty_spaces != 0:
                    temp = str(empty_spaces)
                    fen_pieces += temp
                    empty_spaces = 0

                c = self.pieces[i].color
                t = self.pieces[i].type
                piece_str = str(c.value + t.value)
                fen_pieces += piece_str_to_fen_letter(piece_str)

            if i % 8 == 7:
                if empty_spaces != 0:
                    fen_pieces += str(empty_spaces)
                    empty_spaces = 0
                if i != 63:
                    fen_pieces += "/"

        self.fen._pieces = fen_pieces

        if self.current_turn == Color.WHITE:
            self.fen._turn = "b"
        else:
            self.fen._turn = "w"

        self.fen.update()

    def update_game(self, pick_id, drop_id) -> None:
        """Updates game variables."""
        if self.is_running:
            now = datetime.datetime.now(tz=timezone.utc)
            time_dif = now - self.last_move_time
            time_dif_seconds = int(time_dif.seconds)
            if self.current_turn == Color.WHITE:
                self.timer_white -= time_dif_seconds
            elif self.current_turn == Color.BLACK:
                self.timer_black -= time_dif_seconds
            self.last_move_time = now
        else:
            self.is_running = True
            now = datetime.datetime.now(tz=timezone.utc)
            self.start_time = now
            self.last_move_time = now

        self.game_positions.append(self.fen.fen)
        self.move_timestamps.append(self.timers)
        self.move_history.append((pick_id, drop_id))

    def end_move(self, pick_id, drop_id) -> dict[str, any]:
        """Handler for the after move mechanics."""
        if self.current_turn == Color.BLACK:
            self.fen._fullmoves = self.fen.fullmoves + 1
        else:
            self.fen._fullmoves = self.fen.fullmoves

        self.prev_pick_id = pick_id
        self.prev_drop_id = drop_id
        self.update_fen()
        self.update_game(pick_id, drop_id)
        self.save_game_pickle()

        if self.is_game_finished():
            self.end_game()
            return self.get_game_end_msg()
        else:
            return self.get_move_msg()

    def move_cancel_handler(self) -> None:
        """Handler for the move cancelling mechanics."""
        index = self.game_positions.index(self.move_cancel_fen)

        self.game_positions = self.game_positions[: (index + 1)]
        self.move_timestamps = self.move_timestamps[: (index + 1)]
        self.move_history = self.move_history[: (index + 1)]

        timers = to_seconds(self.move_timestamps[-1])
        self.timer_white = int(timers[0])
        self.timer_black = int(timers[1])

        self.fen = FEN(self.move_cancel_fen)
        self.last_move_time = datetime.datetime.now(tz=timezone.utc)
        self.move_cancel_fen = None
        self.save_game_pickle()

    def end_game(self, game_result=None) -> None:
        """Ends the game and saves it to database."""
        now = datetime.datetime.now(tz=timezone.utc)
        self.end_time = now

        if game_result:
            self.game_result = game_result

        # if self.game_result not in (GameResult.WHITEWINS_OOT, GameResult.BLACKWINS_OOT):
        #     for task in asyncio.all_tasks():
        #         if task.get_name() == f"{self.uuid}_clock":
        #             task.cancel()

        loop = None

        if self.game_result in (
            GameResult.WHITEWINS_ABANDONED,
            GameResult.BLACKWINS_ABANDONED,
        ):
            if self.is_running:
                time_dif = now - self.last_move_time
                time_dif_seconds = int(time_dif.seconds)
                if self.current_turn == Color.WHITE:
                    self.timer_white -= time_dif_seconds
                elif self.current_turn == Color.BLACK:
                    self.timer_black -= time_dif_seconds
                self.move_timestamps[-1] = self.timers

                if self.game_result == GameResult.BLACKWINS_ABANDONED:
                    self.winner_id = self.players["black"]
                elif self.game_result == GameResult.WHITEWINS_ABANDONED:
                    self.winner_id = self.players["white"]
            else:
                self.game_result = GameResult.DRAW_ABANDONED
                self.winner_id = None

        elif self.game_result == GameResult.WHITEWINS_OOT:
            self.winner_id = self.players["white"]
            self.timer_black = 0

        elif self.game_result == GameResult.BLACKWINS_OOT:
            self.winner_id = self.players["black"]
            self.timer_white = 0

        elif self.game_result == GameResult.WHITEWINS_MATE:
            self.winner_id = self.players["white"]

        elif self.game_result == GameResult.BLACKWINS_MATE:
            self.winner_id = self.players["black"]

        elif self.game_result == GameResult.DRAW_STALEMATE:
            self.winner_id = None

        elif self.game_result == GameResult.DRAW_THREEFOLD_REP:
            self.winner_id = None

        elif self.game_result == GameResult.DRAW_50_MOVES:
            self.winner_id = None

        elif self.game_result == GameResult.DRAW_AGREEMENT:
            if self.is_running:
                time_dif = now - self.last_move_time
                time_dif_seconds = int(time_dif.seconds)
                if self.current_turn == Color.WHITE:
                    self.timer_white -= time_dif_seconds
                elif self.current_turn == Color.BLACK:
                    self.timer_black -= time_dif_seconds
                self.move_timestamps[-1] = self.timers

            self.winner_id = None

        elif self.game_result in (
            GameResult.WHITEWINS_RESIGNED,
            GameResult.BLACKWINS_RESIGNED,
        ):
            if self.is_running:
                time_dif = now - self.last_move_time
                time_dif_seconds = int(time_dif.seconds)
                if self.current_turn == Color.WHITE:
                    self.timer_white -= time_dif_seconds
                elif self.current_turn == Color.BLACK:
                    self.timer_black -= time_dif_seconds
                self.move_timestamps[-1] = self.timers
                if self.game_result == GameResult.WHITEWINS_RESIGNED:
                    self.winner_id = self.players["white"]
                elif self.game_result == GameResult.BLACKWINS_RESIGNED:
                    self.winner_id = self.players["black"]
            else:
                self.game_result = GameResult.DRAW_ABANDONED
                self.winner_id = None

        self.is_running = False

        self.save_game_pickle()

    def is_threefold_repetition(self) -> bool:
        """Checks for a threefold repetition."""
        current_cut_position = f"{self.fen.pieces} {self.fen.turn} {self.fen.castles}"
        cut_game_positions = []
        for fen in self.game_positions:
            fen_obj = FEN(fen)
            cut_position = f"{fen_obj.pieces} {fen_obj.turn} {fen_obj.castles}"
            cut_game_positions.append(cut_position)
        cut_game_positions.append(current_cut_position)
        if cut_game_positions.count(current_cut_position) > 2:
            return True
        else:
            return False

    def is_game_finished(self) -> bool:
        """Check if the game is finished. If it is, set the proper self.game_result and return True, else return False."""
        if not self.is_any_move_possible():
            if self.is_checked():
                if self.current_turn == Color.WHITE:
                    self.game_result = GameResult.BLACKWINS_MATE
                    return True
                elif self.current_turn == Color.BLACK:
                    self.game_result = GameResult.WHITEWINS_MATE
                    return True
            else:
                self.game_result = GameResult.DRAW_STALEMATE
                return True
        else:
            if self.fen.halfmoves == 50:
                self.game_result = GameResult.DRAW_50_MOVES
                return True
            elif self.is_threefold_repetition():
                self.game_result = GameResult.DRAW_THREEFOLD_REP
                return True
            else:
                return False

    def is_any_move_possible(self) -> bool:
        """Return True if the current player has any legal moves, else return False."""
        for i in range(64):
            if self.pieces[i] is not None and self.pieces[i].color == self.current_turn:
                self.update_possible_moves(i)
                for j in range(64):
                    if (
                        self.possible_moves[j] is True
                        and self.is_checked_nextmove(i, j) is False
                    ):
                        return True
        else:
            return False

    def promotion_handler(self, piece_type) -> dict[str, any]:
        """Handler for the promotion mechanics. """
        piece_type = PieceType(piece_type)
        pick_id, drop_id = self.get_promotion_pick()
        self.pieces[pick_id] = None
        self.pieces[drop_id] = Piece(self.current_turn, piece_type)
        return self.end_move(pick_id, drop_id)

    def get_model_data(self) -> dict[str, any]:
        """Get model data to be saved to db."""
        if not self.is_running:
            self.start_time = self.end_time = datetime.datetime.now(tz=timezone.utc)
        return {
            "player_white_id": self.players["white"],
            "player_black_id": self.players["black"],
            "winner_id": self.winner_id,
            "game_positions": self.get_game_positions_str(),
            "move_timestamps": self.get_move_timestamps_str(),
            "move_history": self.get_move_history_str(),
            "game_result": self.game_result,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }

    def get_promotion_pick(self) -> tuple[int, int]:
        """Returns variables saved in save_promotion_pick() and sets them to None."""
        pick_id = self.promotion_pick_id
        drop_id = self.promotion_drop_id
        self.promotion_pick_id = None
        self.promotion_drop_id = None
        return pick_id, drop_id

    def get_init_msg(self) -> dict[str, any]:
        return {
            "type": "init",
            "fen": self.fen.fen,
            "time_white": self.timers[0],
            "time_black": self.timers[1],
            "game_positions": self.game_positions,
        }

    def get_game_end_msg(self) -> dict[str, any]:
        return {
            "type": "game_end",
            "fen": self.fen.fen,
            "time_white": self.timers[0],
            "time_black": self.timers[1],
            "game_result": self.game_result.value,
            "game_positions": self.game_positions,
        }

    def get_move_msg(self) -> dict[str, any]:
        return {
            "type": "move",
            "fen": self.fen.fen,
            "time_white": self.timers[0],
            "time_black": self.timers[1],
            "game_positions": self.game_positions,
        }

    def get_promoting_msg(self) -> dict[str, any]:
        return {"type": "promoting"}

    def update_possible_moves(self, p) -> None:
        self.possible_moves = [False] * 64

        picked_type = self.pieces[p].type

        if picked_type == PieceType.PAWN:
            self.pawn_moves(p)

        elif picked_type == PieceType.KNIGHT:
            self.knight_moves(p)

        elif picked_type == PieceType.BISHOP:
            self.bishop_moves(p)

        elif picked_type == PieceType.ROOK:
            self.rook_moves(p)

        elif picked_type == PieceType.QUEEN:
            self.queen_moves(p)

        elif picked_type == PieceType.KING:
            self.king_moves(p)

    def pawn_moves(self, p) -> None:
        c = self.pieces[p].color

        if c == Color.WHITE:
            # 1 field up
            if p - 8 >= 0 and self.pieces[p - 8] is None:
                self.possible_moves[p - 8] = True
                # 2 fields up
                if (
                    p - 16 >= 0
                    and (p >= 48 and p <= 55)
                    and self.pieces[p - 16] is None
                ):
                    self.possible_moves[p - 16] = True
            # diagonal up-left
            if (
                p - 9 >= 0
                and p % 8 != 0
                and self.pieces[p - 9] is not None
                and self.pieces[p - 9].color != c
            ):
                self.possible_moves[p - 9] = True
            # diagonal up-right
            if (
                p - 7 >= 0
                and p % 8 != 7
                and self.pieces[p - 7] is not None
                and self.pieces[p - 7].color != c
            ):
                self.possible_moves[p - 7] = True

        if c == Color.BLACK:
            # 1 field down
            if p + 8 < 64 and self.pieces[p + 8] is None:
                self.possible_moves[p + 8] = True
                # 2 fields down
                if p + 16 < 64 and (p >= 8 and p <= 15) and self.pieces[p + 16] is None:
                    self.possible_moves[p + 16] = True
            # diagonal down-right
            if (
                p + 9 < 64
                and p % 8 != 7
                and self.pieces[p + 9] is not None
                and self.pieces[p + 9].color != c
            ):
                self.possible_moves[p + 9] = True
            # diagonal down-left
            if (
                p + 7 < 64
                and p % 8 != 0
                and self.pieces[p + 7] is not None
                and self.pieces[p + 7].color != c
            ):
                self.possible_moves[p + 7] = True

    def knight_moves(self, p) -> None:
        c = self.pieces[p].color

        patterns = (-10, 6, -17, 15, -15, 17, -6, 10)
        start = 0
        end = 8
        if p % 8 == 0:
            start = 4
        if p % 8 == 1:
            start = 2
        if p % 8 == 6:
            end = 6
        if p % 8 == 7:
            end = 4
        for i in range(start, end):
            trgt = p + patterns[i]
            if (
                trgt >= 0
                and trgt < 64
                and (self.pieces[trgt] is None or self.pieces[trgt].color != c)
            ):
                self.possible_moves[trgt] = True

    def bishop_moves(self, p) -> None:
        c = self.pieces[p].color

        patterns = (9, 7, -9, -7)
        origin_p = p
        for i in range(4):
            p = origin_p
            while p >= 0 and p < 64:
                if (
                    p + patterns[i] < 0
                    or p + patterns[i] > 63
                    or (p % 8 == 0 and (patterns[i] == -9 or patterns[i] == 7))
                    or (p % 8 == 7 and (patterns[i] == -7 or patterns[i] == 9))
                    or (
                        self.pieces[p + patterns[i]] is not None
                        and self.pieces[p + patterns[i]].color == c
                    )
                ):
                    break
                if (
                    self.pieces[p + patterns[i]] is not None
                    and self.pieces[p + patterns[i]].color != c
                ):
                    p += patterns[i]
                    self.possible_moves[p] = True
                    break
                p += patterns[i]
                self.possible_moves[p] = True

    def rook_moves(self, p) -> None:
        c = self.pieces[p].color

        patterns = (8, -8, 1, -1)
        origin_p = p
        for i in range(2):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] > 63 or p + patterns[i] < 0:
                    break
                if self.pieces[p + patterns[i]] is not None:
                    if self.pieces[p + patterns[i]].color != c:
                        p += patterns[i]
                        self.possible_moves[p] = True
                        break
                    break
                p += patterns[i]
                self.possible_moves[p] = True

        for i in range(2, 4):
            p = origin_p
            while p >= 0 and p < 64:
                if (patterns[i] == -1 and p % 8 == 0) or (
                    patterns[i] == 1 and p % 8 == 7
                ):
                    break
                if self.pieces[p + patterns[i]] is not None:
                    if self.pieces[p + patterns[i]].color != c:
                        p += patterns[i]
                        self.possible_moves[p] = True
                        break
                    break
                p += patterns[i]
                self.possible_moves[p] = True

    def queen_moves(self, p) -> None:
        self.rook_moves(p)
        self.bishop_moves(p)

    def king_moves(self, p) -> None:
        c = self.pieces[p].color
        start = 0
        end = 8
        patterns = (-9, -1, 7, -8, 8, -7, 1, 9)
        if p % 8 == 0:
            start = 3
        if p % 8 == 7:
            end = 5

        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                if self.pieces[trgt] is None or self.pieces[trgt].color != c:
                    self.possible_moves[trgt] = True

        self.update_possible_castles(p)

    def pawn_fields(self, p) -> None:
        c = self.pieces[p].color
        if c == Color.WHITE:
            if p - 9 >= 0 and p % 8 != 0:
                self.attacked_fields[p - 9] = True
            if p - 7 >= 0 and p % 8 != 7:
                self.attacked_fields[p - 7] = True

        if c == Color.BLACK:
            if p + 9 < 63 and p % 8 != 7:
                self.attacked_fields[p + 9] = True
            if p + 7 < 63 and p % 8 != 0:
                self.attacked_fields[p + 7] = True

    def knight_fields(self, p) -> None:
        patterns = (-10, 6, -17, 15, -15, 17, -6, 10)
        start = 0
        end = 8

        if p % 8 == 0:
            start = 4

        if p % 8 == 1:
            start = 2

        if p % 8 == 6:
            end = 6

        if p % 8 == 7:
            end = 4

        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                self.attacked_fields[trgt] = True

    def bishop_fields(self, p) -> None:
        patterns = (9, 7, -9, -7)
        origin_p = p
        for i in range(4):
            p = origin_p
            while p >= 0 and p < 64:
                if (
                    p + patterns[i] < 0
                    or p + patterns[i] > 63
                    or (p % 8 == 0 and (patterns[i] == -9 or patterns[i] == 7))
                    or (p % 8 == 7 and (patterns[i] == -7 or patterns[i] == 9))
                ):
                    break
                if self.pieces[p + patterns[i]] is not None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

    def rook_fields(self, p) -> None:
        patterns = (8, -8, 1, -1)
        origin_p = p
        for i in range(2):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] > 63 or p + patterns[i] < 0:
                    break
                if self.pieces[p + patterns[i]] is not None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

        for i in range(2, 4):
            p = origin_p
            while p >= 0 and p < 64:
                if (
                    p + patterns[i] > 63
                    or p + patterns[i] < 0
                    or (patterns[i] == -1 and p % 8 == 0)
                    or (patterns[i] == 1 and p % 8 == 7)
                ):
                    break
                if self.pieces[p + patterns[i]] is not None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

    def queen_fields(self, p) -> None:
        self.rook_fields(p)
        self.bishop_fields(p)

    def king_fields(self, p) -> None:
        start = 0
        end = 8
        patterns = (-9, -1, 7, -8, 8, -7, 1, 9)

        if p % 8 == 0:
            start = 4
        if p % 8 == 7:
            end = 5
        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                self.attacked_fields[trgt] = True

    def update_attacked_fields(self) -> None:
        """Updates the fields that are being attacked by opponent."""
        opponent_color = opposite_color(self.current_turn)
        self.attacked_fields = [False] * 64
        for p in range(64):
            if self.pieces[p] is not None and self.pieces[p].color == opponent_color:
                if self.pieces[p].type == PieceType.PAWN:
                    self.pawn_fields(p)
                elif self.pieces[p].type == PieceType.KNIGHT:
                    self.knight_fields(p)
                elif self.pieces[p].type == PieceType.BISHOP:
                    self.bishop_fields(p)
                elif self.pieces[p].type == PieceType.ROOK:
                    self.rook_fields(p)
                elif self.pieces[p].type == PieceType.QUEEN:
                    self.queen_fields(p)
                elif self.pieces[p].type == PieceType.KING:
                    self.king_fields(p)

    def update_possible_castles(self, p) -> None:
        c = self.pieces[p].color
        self.update_attacked_fields()
        if c == Color.WHITE:
            indexes_pieces = (57, 58, 59)
            indexes_fields = (58, 59)
            outcome_pieces = [self.pieces[i] for i in indexes_pieces]
            outcome_fields = [self.attacked_fields[i] for i in indexes_fields]

            if (
                all(x is None for x in outcome_pieces) is True
                and all(x is False for x in outcome_fields) is True
                and self.pieces[56] is not None
                and self.pieces[56].color == c
            ):
                self.possible_moves[58] = True

            indexes = (61, 62)

            outcome_pieces = [self.pieces[i] for i in indexes]
            outcome_fields = [self.attacked_fields[i] for i in indexes]

            if (
                all(x is None for x in outcome_pieces) is True
                and all(x is False for x in outcome_fields) is True
                and self.pieces[63] is not None
                and self.pieces[63].color == c
            ):
                self.possible_moves[62] = True

        if c == Color.BLACK:
            indexes_pieces = (1, 2, 3)
            indexes_fields = (2, 3)
            outcome_pieces = [self.pieces[i] for i in indexes_pieces]
            outcome_fields = [self.attacked_fields[i] for i in indexes_fields]

            if (
                all(x is None for x in outcome_pieces) is True
                and all(x is False for x in outcome_fields) is True
                and self.pieces[0] is not None
                and self.pieces[0].color == c
            ):
                self.possible_moves[2] = True

            indexes = (5, 6)

            outcome_pieces = [self.pieces[i] for i in indexes]
            outcome_fields = [self.attacked_fields[i] for i in indexes]

            if (
                all(x is None for x in outcome_pieces) is True
                and all(x is False for x in outcome_fields) is True
                and self.pieces[7] is not None
                and self.pieces[7].color == c
            ):
                self.possible_moves[6] = True
