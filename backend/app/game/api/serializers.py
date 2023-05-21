from game.models import Game, FreeBoardGame
from rest_framework import serializers
from stockfish import Stockfish

stockfish = Stockfish(path='/usr/games/stockfish')


class GameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    game_positions = serializers.ListField(source='get_game_positions')
    move_timestamps = serializers.ListField(source='get_move_timestamps')
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'game_positions', 'move_timestamps')

class FreeBoardGameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    game_positions = serializers.ListField(source='get_game_positions')

    class Meta:
        model = Game
        fields = ('id', 'game_positions')

class FreeBoardGameCreateSerializer(serializers.ModelSerializer):
    fen = serializers.CharField()

    def validate(self, settings):
        fen = settings.get('fen')
        if not stockfish.is_fen_valid(fen):
            raise serializers.ValidationError({"fen": "Given FEN is not valid."})
        return settings
    
    def create(self, validated_data):
        return FreeBoardGame.objects.new_freeboard_game(validated_data)
    
    class Meta:
        model = FreeBoardGame
        fields= ('fen',)

class GameHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    game_end_time = serializers.DateTimeField()
    
    class Meta:
        model = Game
        fields = ('id', 'player_white', 'player_black', 'winner', 'game_end_time')