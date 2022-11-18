from rest_framework import serializers
from game.models import Game

class GameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    game_positions = serializers.ListField(source='get_game_positions')
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'game_positions')

class GameHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner')