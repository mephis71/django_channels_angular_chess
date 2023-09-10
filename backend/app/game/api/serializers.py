from django.contrib.auth import get_user_model
from game.api.validators import is_fen_valid
from game.game_engine.stockfish import stockfish
from game.models import FreeBoardGame, GameInProgress, GameLive, GamePuzzle
from rest_framework import serializers

User = get_user_model()


class RetrieveGameInProgressSerializer(serializers.ModelSerializer):
    player_white_id = serializers.ReadOnlyField(source="player_white.id")
    player_black_id = serializers.ReadOnlyField(source="player_black.id")

    class Meta:
        model = GameInProgress
        fields = (
            "id",
            "player_white_id",
            "player_black_id",
        )

        read_only_fields = ("id",)


class CreateGameLiveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())
    player_black = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())
    winner = serializers.PrimaryKeyRelatedField(required=False, write_only=True, queryset=User.objects.all())
    game_positions = serializers.ListField(write_only=True)
    move_timestamps = serializers.ListField(write_only=True)
    move_history = serializers.ListField(write_only=True)
    start_time = serializers.DateTimeField(write_only=True)
    end_time = serializers.DateTimeField(write_only=True)
    duration = serializers.IntegerField(write_only=True)

    class Meta:
        model = GameLive
        fields = (
            "id",
            "player_white",
            "player_black",
            "winner",
            "game_positions",
            "move_timestamps",
            "move_history",
            "start_time",
            "end_time",
            "duration",
        )

    def create(self, validated_data):
        return GameLive.objects.create_game(validated_data)


class RetrieveGameLiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameLive
        fields = (
            "id",
            "player_white",
            "player_black",
            "winner_id",
            "game_positions",
            "move_timestamps",
            "move_history",
            "start_time",
            "end_time",
            "duration",
        )
        read_only_fields = (
            "id",
            "player_white",
            "player_black",
            "winner_id",
            "game_positions",
            "move_timestamps",
            "move_history",
            "start_time",
            "end_time",
            "duration",
        )


class CreateGamePuzzleSerializer(serializers.ModelSerializer):
    fen = serializers.CharField(write_only=True, validators=[is_fen_valid])

    class Meta:
        model = GamePuzzle
        fields = ("id", "fen", "url")
        read_only_fields = ("id", "url")


class RetrieveGamePuzzleSerializer(serializers.ModelSerializer):
    fen = serializers.CharField(validators=[is_fen_valid])

    class Meta:
        model = GamePuzzle
        fields = ("id", "fen", "player_color")
        read_only_fields = ("id", "fen", "player_color")


class FreeBoardGameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    game_positions = serializers.ListField(source="get_game_positions", read_only=True)
    fen = serializers.CharField()

    def validate(self, settings):
        fen = settings.get("fen")
        if not stockfish.is_fen_valid(fen):
            raise serializers.ValidationError({"fen": "Given FEN is not valid."})
        return settings

    class Meta:
        model = FreeBoardGame
        fields = ("id", "game_positions", "fen")


class GameHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    player_white = serializers.CharField()
    player_black = serializers.CharField()
    winner = serializers.CharField()
    end_time = serializers.DateTimeField()

    class Meta:
        model = GameLive
        fields = ("id", "player_white", "player_black", "winner", "end_time")
