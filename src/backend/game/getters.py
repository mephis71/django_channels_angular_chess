from channels.db import database_sync_to_async
from .models import Game

@database_sync_to_async
def get_game_by_id(game_id):
    return Game.objects.select_related("player_white", "player_black").get(id=game_id)

def new_game(usernames, settings):
    game_obj = Game.objects.new_game(usernames, settings)
    return Game.objects.select_related("player_white", "player_black").get(id=game_obj.id)