from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from rich import print



#Create your models here.

class GameManager(models.Manager):
    def get_or_new(self, username1, username2):
        qlookup1 = Q(player1__username = username1) & Q(player2__username = username2)
        qlookup2 = Q(player1__username = username2) & Q(player2__username = username1)

        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() != 0:
            return qs[0]
        else:
            p1 = User.objects.get(username = username1)
            p2 = User.objects.get(username = username2)
            obj = self.model(player1 = p1, player2 = p2)
            obj.save()
            return obj
         

class Game(models.Model):
    DEFAULT_GAME_STATE = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    STARTING_PLAYER = 'white'
    DEFAULT_SECONDS = 600
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='first')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='second')
    game_state = models.TextField(default=DEFAULT_GAME_STATE)
    turn = models.TextField(default=STARTING_PLAYER)
    timer_black = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    timer_white = models.PositiveIntegerField(default = DEFAULT_SECONDS)
    is_running = models.BooleanField(default=False)

    objects = GameManager()

    connected_players = {
        'white': None,
        'black': None
    }

    def get_game_name(self):
        return f'game_{self.id}'        

    def get_color(self,player):
        players = self.connected_players
        for key in players:
            if players[key] == player:
                return key

    def add_player(self, username):
        players = self.connected_players
        for key in players:
            if players[key] == username:
                return
            elif players[key] is None:
                players[key] = username
                break
        self.save()

    def remove_player(self, username):
        players = self.connected_players
        for key in players:
            if players[key] == username:
                players[key] = None
                break
        self.save()

    


    








    