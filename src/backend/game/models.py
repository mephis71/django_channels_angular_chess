import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from users.models import UserProfile
from .utils import to_timer_format

User = get_user_model()

class GameManager(models.Manager):
    def get_or_new(self, username1, username2):
        qlookup1 = Q(player_white__username = username1) & Q(player_black__username = username2)
        qlookup2 = Q(player_white__username = username2) & Q(player_black__username = username1)

        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() != 0 and qs[0].is_finished == False:
            return qs[0]
        else:
            obj = self.model()
            obj.save()
            return obj

class Game(models.Model):
    # default values
    DEFAULT_GAME_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    STARTING_PLAYER = 'white'
    DEFAULT_SECONDS = 300

    # players
    player_white = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='first', null=True)
    player_black = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='second', null=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='winner', default=None, null=True)

    # game info
    fen = models.TextField(default=DEFAULT_GAME_FEN)
    timer_black = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    timer_white = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    is_running = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    game_positions = models.TextField(default=DEFAULT_GAME_FEN, null=False)
    move_timestamps = models.TextField(default=f'{DEFAULT_SECONDS}-{DEFAULT_SECONDS}')
    endgame_cause = models.TextField(null=True)
    game_start_time = models.DateTimeField(default=None, null=True)
    last_move_time = models.DateTimeField(default=None, null=True)
    game_end_time = models.DateTimeField(default=None, null=True)

    objects = GameManager()

    def get_game_positions(self):
        return self.game_positions.split(';')

    def get_move_timestamps(self):
        pairs = self.move_timestamps.split(';')
        output = []
        for pair in pairs:
            pair = pair.split('-')
            pair = [to_timer_format(pair[0]), to_timer_format(pair[1])]
            output.append(pair)
        return output

    def get_turn(self):
        fen = self.fen
        fen = fen.split()
        fen_turn = fen[1]
        if fen_turn == 'w':
            return 'white'
        elif fen_turn == 'b':
            return 'black'

    def get_game_name(self):
        return f'game_{self.id}'        

    def get_color(self, username):
        if self.player_white.username == username:
            return 'white'
        elif self.player_black.username == username:
            return 'black'
        else:
            raise Exception(f'Username not matched: {username}')
    
    def assign_colors_randomly(self, username1, username2):
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        number = random.randint(1, 2)
        print('losowanie:', number)
        if number == 1:
            self.player_white = user1 
            self.player_black = user2
        elif number == 2:
            self.player_white = user2
            self.player_black = user1
        self.save()

    def add_to_history(self):
        UserProfile.objects.get(pk=self.player_white.pk).game_history.add(self)
        UserProfile.objects.get(pk=self.player_black.pk).game_history.add(self)
