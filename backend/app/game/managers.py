from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class GameLiveManager(models.Manager):
    def create_game(self, validated_data):
        if validated_data['winner_id']:
            game_obj = self.create(**validated_data)
        else:
            validated_data.pop("winner_id")
            game_obj = self.create(**validated_data)
            game_obj.winner = None
            game_obj.save()
            
        return game_obj
