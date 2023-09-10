


import os
from pathlib import Path
import pickle
import random
from django_chess.settings import BASE_DIR
from game.game_engine.game_engine import GameEngine
from game.models import GameInProgress, User
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

def assigned_colors_randomly(players):
    number = random.randint(1, 2)
    if number == 1:
        return {"white": players[0], "black": players[1]}
    elif number == 2:
        return {"white": players[1], "black": players[0]}

def assigned_colors(settings):
    return {
        "white": settings["white_id"],
        "black": settings["black_id"]
    }

def start_game(game_info):
    players = game_info["players"]
    settings = game_info["settings"]
    random_colors = settings['random_colors']
    duration = settings['duration']

    if random_colors:
        players_dict = assigned_colors_randomly(players)

    game = GameEngine(players=players_dict, duration=duration, random_colors=random_colors)

    folder_path_str = os.path.join(BASE_DIR, "game/game_pickles")
    folder_path = Path(folder_path_str)
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path_str = os.path.join(
        BASE_DIR, f"game/game_pickles/{game.file_name}.pickle"
    )
    file_path = Path(file_path_str)
    file_path.touch(exist_ok=True)

    with file_path.open("wb") as file:
        pickle.dump(game, file, pickle.HIGHEST_PROTOCOL)


    player_white = User.objects.get(id=players_dict["white"])
    player_black = User.objects.get(id=players_dict["black"])

    game_db_obj = GameInProgress.objects.create(
        uuid=game.uuid, player_white=player_white, player_black=player_black
    )

    msg = {"type": "game_invite_accept", "game_id": game_db_obj.id}

    for id in players:
        async_to_sync(channel_layer.group_send)(
            f"{id}_system", {"type": "system_message", "text": msg}
        )

    return game_db_obj

@database_sync_to_async
def start_game_as_async(game_info):
    players = game_info["players"]
    settings = game_info["settings"]
    random_colors = settings['random_colors']
    duration = settings['duration']

    if random_colors:
        players_dict = assigned_colors_randomly(players)

    game = GameEngine(players=players_dict, duration=duration, random_colors=random_colors)

    folder_path_str = os.path.join(BASE_DIR, "game/game_pickles")
    folder_path = Path(folder_path_str)
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path_str = os.path.join(
        BASE_DIR, f"game/game_pickles/{game.file_name}.pickle"
    )
    file_path = Path(file_path_str)
    file_path.touch(exist_ok=True)

    with file_path.open("wb") as file:
        pickle.dump(game, file, pickle.HIGHEST_PROTOCOL)


    player_white = User.objects.get(id=players_dict["white"])
    player_black = User.objects.get(id=players_dict["black"])

    game_db_obj = GameInProgress.objects.create(
        uuid=game.uuid, player_white=player_white, player_black=player_black
    )

    msg = {"type": "game_invite_accept", "game_id": game_db_obj.id}

    for id in players:
        async_to_sync(channel_layer.group_send)(
            f"{id}_system", {"type": "system_message", "text": msg}
        )

    return game_db_obj