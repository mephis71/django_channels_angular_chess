from rest_framework import serializers
from game.models import Game

class GameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    moves_list = serializers.ListField(source='get_moves_list')
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'moves_list')

class GameHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner')