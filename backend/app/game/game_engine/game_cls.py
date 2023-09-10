from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


class GameResult(Enum):
    # WINS
    WHITEWINS_MATE = "whitewins-mate"
    BLACKWINS_MATE = "blackwins-mate"
    WHITEWINS_OOT = "whitewins-oot"
    BLACKWINS_OOT = "blackwins-oot"
    WHITEWINS_ABANDONED = "whitewins-abandoned"
    BLACKWINS_ABANDONED = "blackwins-abandoned"
    WHITEWINS_RESIGNED = "whitewins-resigned"
    BLACKWINS_RESIGNED = "blackwins-resigned"

    # DRAWS
    DRAW_AGREEMENT = "draw-agreement"
    DRAW_ABANDONED = "draw-abandoned"
    DRAW_STALEMATE = "draw-stalemate"
    DRAW_THREEFOLD_REP = "draw-threefold-rep"
    DRAW_50_MOVES = "draw-50-moves"


@dataclass
class Piece:
    color: Color
    type: PieceType


@dataclass
class FEN:
    fen: str

    @property
    def turn_color(self):
        """Returns the color of the player whose turn it is from FEN."""
        fen = self.fen.split()
        fen_turn = fen[1]
        if fen_turn == "w":
            return Color.WHITE
        elif fen_turn == "b":
            return Color.BLACK

    @property
    def pieces(self):
        """Returns the pieces part from FEN."""
        fen = self.fen.split()
        return fen[0]

    @property
    def turn(self):
        """Returns the turn part from FEN."""
        fen = self.fen.split()
        return fen[1]

    @property
    def castles(self):
        """Returns the castles part from FEN."""
        fen = self.fen.split()
        return fen[2]

    @property
    def enpassant(self):
        """Returns the en passant part from FEN."""
        fen = self.fen.split()
        return fen[3]

    @property
    def halfmoves(self):
        """Returns the halfmoves part from FEN."""
        fen = self.fen.split()
        return int(fen[4])

    @property
    def fullmoves(self):
        """Returns the fullmoves part from FEN."""
        fen = self.fen.split()
        return int(fen[5])

    # Variables that come to life after self.update()
    _pieces: str = None
    _turn: str = None
    _castles: str = None
    _castles_to_pop: str = ""
    _enpassant: str = None
    _halfmoves: int = 0
    _fullmoves: int = 1

    def update(self):
        new_fen_castles = self.castles

        if self._castles_to_pop:
            new_fen_castles = [*new_fen_castles]

            for letter in self._castles_to_pop:
                if letter in new_fen_castles:
                    new_fen_castles.remove(letter)

            new_fen_castles = "".join(new_fen_castles)

        if not new_fen_castles:
            self._castles = "-"
        else:
            self._castles = new_fen_castles

        self.fen = f"{self._pieces} {self._turn} {self._castles} {self._enpassant} {self._halfmoves} {self._fullmoves}"
        self._pieces = None
        self._turn = None
        self._castles = None
        self._castles_to_pop = ""
        self._enpassant = None
        self._halfmoves = 0
        self._fullmoves = 1
