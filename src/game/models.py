import random
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class GameManager(models.Manager):
    def get_or_new(self, username1, username2):
        qlookup1 = Q(player_white__username = username1) & Q(player_black__username = username2)
        qlookup2 = Q(player_white__username = username2) & Q(player_black__username = username1)

        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() != 0:
            return qs[0]
        else:
            obj = self.model()
            obj.save()
            return obj

class Game(models.Model):
    # default values
    DEFAULT_GAME_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    STARTING_PLAYER = 'white'
    DEFAULT_SECONDS = 600

    # players
    player_white = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='first', null=True)
    player_black = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='second', null=True)

    # game info
    fen = models.TextField(default=DEFAULT_GAME_FEN)
    timer_black = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    timer_white = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    is_running = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='winner', default=None, null=True)

    objects = GameManager()

    reset_votes = {
        'white': False,
        'black': False
    }  

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

    def get_color(self, player):
        if self.player_white.username == player:
            return 'white'
        elif self.player_black.username == player:
            return 'black'

    def vote_for_reset(self, color):
        if color == 'white':
            self.reset_votes['white'] = True
        else:
            self.reset_votes['black'] = True
        self.save()

    def check_for_reset(self):
        if self.reset_votes['white'] == True and self.reset_votes['black'] == True:
            return True
        else:
            return False
    
    def assign_colors_randomly(self, username1, username2):
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        number = random.randint(1, 2)
        if number == 1:
            self.player_white = user1 
            self.player_black = user2
        elif number == 2:
            self.player_white = user2
            self.player_black = user1
        self.save()
