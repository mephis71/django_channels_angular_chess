import pytest
from django.contrib.auth import get_user_model
from game.models import GameLive
from game.game_engine.game_cls import GameResult
from game.game_engine.game_engine import GameEngine

from .factories import UserFactory

User = get_user_model()


@pytest.mark.parametrize(
    "init_fen, end_fen, moves, game_result",
    [
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "r1q1kbnr/2pbpQpp/ppN5/8/2BpP3/8/PPPP1PPP/RNB1K2R b KQkq - 0 8",
            (
                (52, 36),
                (11, 27),
                (62, 45),
                (1, 18),
                (61, 25),
                (8, 16),
                (25, 34),
                (2, 11),
                (45, 35),
                (3, 2),
                (59, 45),
                (9, 17),
                (35, 18),
                (27, 35),
                (45, 13),
            ),
            GameResult.WHITEWINS_MATE,
        ),
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "2k4r/1pp2Npp/2P1pp2/P4b2/P7/2b2nP1/RB1r1P2/4KB1R w K - 2 18",
            (
                ("52", "36"),
                ("11", "27"),
                ("36", "27"),
                ("1", "18"),
                ("27", "18"),
                ("2", "29"),
                ("62", "47"),
                ("3", "19"),
                ("47", "30"),
                ("4", "2"),
                ("59", "38"),
                ("8", "16"),
                ("49", "41"),
                ("16", "24"),
                ("58", "49"),
                ("19", "51"),
                ("57", "51"),
                ("12", "20"),
                ("48", "40"),
                ("5", "33"),
                ("50", "42"),
                ("33", "42"),
                ("41", "33"),
                ("6", "21"),
                ("33", "24"),
                ("21", "38"),
                ("54", "46"),
                ("3", "51"),
                ("40", "32"),
                ("38", "55"),
                ("56", "48"),
                ("13", "21"),
                ("30", "13"),
                ("55", "45"),
            ),
            GameResult.BLACKWINS_MATE,
        ),
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "2kr1bnr/1bQpqpp1/p1n5/4B2p/3PP3/1P3N2/P1P1BPPP/RN3RK1 b - - 0 12",
            (
                ("52", "36"),
                ("12", "28"),
                ("62", "45"),
                ("1", "18"),
                ("61", "52"),
                ("3", "12"),
                ("49", "41"),
                ("9", "17"),
                ("58", "49"),
                ("2", "9"),
                ("60", "62"),
                ("4", "2"),
                ("49", "28"),
                ("8", "16"),
                ("51", "35"),
                ("15", "23"),
                ("59", "51"),
                ("23", "31"),
                ("51", "24"),
                ("7", "15"),
                ("24", "17"),
                ("15", "7"),
                ("17", "10"),
            ),
            GameResult.WHITEWINS_MATE,
        ),
    ],
)
def test_checkmates(game_file_path: str, init_fen, end_fen, moves, game_result):
    player_white = UserFactory(username="testtesttest")
    player_black = UserFactory(username="othertest")
    players = {"white": player_white.id, "black": player_black.id}

    game = GameEngine(players=players, duration=300, init_fen=init_fen)
    game.set_file_path(game_file_path)

    assert game.is_running is False

    for index, move in enumerate(moves):
        if index == 1:
            assert game.is_running is True
        game.make_move(move[0], move[1])

    assert game.is_running is False

    assert game.fen.fen == end_fen
    assert game.fen.fen == game.game_positions[-1]

    assert game.game_result == game_result
    
    model_data = game.get_model_data()
    from rich import print
    print(game)
    game_db_obj = GameLive.objects.create_game(model_data)

    assert game_db_obj.player_white.id == game.players['white']
    assert game_db_obj.player_black.id == game.players['black']
    
    assert game_db_obj.winner.id == game.winner_id

    assert game_db_obj.game_positions == game.get_game_positions_str()
    assert game_db_obj.move_timestamps == game.get_move_timestamps_str()
    assert game_db_obj.move_history == game.get_move_history_str()

    assert list(game_db_obj.get_game_positions()) == game.game_positions
    assert list(game_db_obj.get_move_timestamps()) == game.move_timestamps
    assert list(game_db_obj.get_move_history()) == game.move_history

    assert game_db_obj.game_result == game.game_result
    assert game_db_obj.start_time == game.start_time
    assert game_db_obj.end_time == game.end_time


# def test_attacked_fields():
#     init_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
#     game = GameEngine(init_fen=init_fen, duration=300, random_colors=True)
#     print(game.attacked_fields)
#     print(game.update_attacked_fields())
#     print(game.attacked_fields)
