from channels.db import database_sync_to_async
from .models import Game

@database_sync_to_async
def get_game_by_id(game_id):
    return Game.objects.select_related("player_white", "player_black").get(id=game_id)

def get_or_create_game(username1, username2):
    game_obj = Game.objects.get_or_new(username1, username2)
    return Game.objects.select_related("player_white", "player_black").get(id=game_obj.id)