from game.models import Game, FreeBoardGame

Game.objects.all().delete()
FreeBoardGame.objects.all().delete()
