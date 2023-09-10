from game.game_engine.stockfish import stockfish
from rest_framework.exceptions import ValidationError


def is_fen_valid(fen: str):
    if not stockfish.is_fen_valid(fen):
        raise ValidationError("Fen is not valid.")
