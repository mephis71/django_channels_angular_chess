from django.contrib.auth import get_user_model
from django.db import models
from game.game_engine.game_vars import DEFAULT_GAME_FEN
from users.models import UserProfile

from .managers import GameManager

User = get_user_model()


class GameInProgress(models.Model):
    uuid = models.UUIDField()
    player_white = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="games_as_white_in_progress",
    )

    player_black = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="games_as_black_in_progress",
    )

    @property
    def file_name(self):
        return f"game_{self.uuid}"

    @property
    def task_name(self):
        return f"game_{self.uuid}"

    @property
    def group_name(self):
        return f"group_{self.uuid}"


class GameBase(models.Model):
    fen = models.TextField(null=False)
    game_positions = models.TextField(null=False)

    def get_game_positions(self):
        return self.game_positions.split(";")

    class Meta:
        abstract = True


class Game(GameBase):
    # Players
    player_white = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="games_as_white",
    )
    player_black = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="games_as_black",
    )
    winner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="won_games",
        null=True,
    )

    # Game info
    duration = models.PositiveIntegerField()
    move_history = models.TextField()
    move_timestamps = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    game_result = models.TextField()

    objects = GameManager()

    def get_move_timestamps(self):
        """Returns move timestamps in (('05:00', '03:27'), ('04:47', '03:27'), ...) format."""
        timestamps = self.move_timestamps.split(";")
        return tuple([tuple(timestamp.split("-")) for timestamp in timestamps])

    def get_move_history(self):
        """Returns move history in ((8, 16), (6, 20), ...) format."""
        move_history = self.move_history.split(";")
        return tuple([tuple(map(int, move.split("-"))) for move in move_history])

    def get_game_positions(self):
        """Returns game positions in (fen1, fen2, ...) format."""
        return tuple(self.game_positions.split(";"))

    def add_to_history(self):
        UserProfile.objects.get(pk=self.player_white.pk).game_history.add(self)
        UserProfile.objects.get(pk=self.player_black.pk).game_history.add(self)


class FreeBoardGame(GameBase):
    def get_game_name(self):
        return f"freeboard_game_{self.id}"


class GamePuzzle(models.Model):
    fen = models.TextField(default=DEFAULT_GAME_FEN)

    @property
    def url(self):
        return f"/game/puzzle/{self.id}"
