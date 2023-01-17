from game.models import Game
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    game_positions = serializers.ListField(source='get_game_positions')
    move_timestamps = serializers.ListField(source='get_move_timestamps')
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'game_positions', 'move_timestamps')\

class GameHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    game_end_time = serializers.DateTimeField()
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'game_end_time')