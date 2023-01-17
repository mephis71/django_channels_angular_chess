import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from users.models import UserProfile

from .utils import to_timer_format

User = get_user_model()

class GameManager(models.Manager):
    def new_game(self, usernames, settings):
        game_obj = self.model()
        game_obj.apply_settings(usernames, settings)
        game_obj.save()
        return game_obj

    def get_running_games(self, username):
        qs = self.get_queryset().filter(Q(is_running=True) & (Q(player_white__username=username) | Q(player_black__username=username)))
        return qs

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

    duration = models.PositiveIntegerField(null=True)
    random_colors = models.BooleanField(null=True)

    _move_cancel_fen = models.TextField(null=True, default=None)
    _game_result = models.TextField(null=True)

    objects = GameManager()

    def apply_settings(self, usernames, settings):
        if settings['random_colors']:
            self.assign_colors_randomly(usernames)
        else:
            self.player_white = User.objects.get(username=settings['white'])
            self.player_black = User.objects.get(username=settings['black'])

        self.timer_white = self.timer_black = settings['duration'] * 60

        self.duration = settings['duration']
        self.random_colors = settings['random_colors']

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

    def get_raw_move_timestamps(self):
        output = self.move_timestamps.split(';')
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
    
    def assign_colors_randomly(self, usernames):
        user1 = User.objects.get(username=usernames[0])
        user2 = User.objects.get(username=usernames[1])
        number = random.randint(1, 2)
        if number == 1:
            self.player_white = user1 
            self.player_black = user2
        elif number == 2:
            self.player_white = user2
            self.player_black = user1

    def add_to_history(self):
        UserProfile.objects.get(pk=self.player_white.pk).game_history.add(self)
        UserProfile.objects.get(pk=self.player_black.pk).game_history.add(self)

    

    
