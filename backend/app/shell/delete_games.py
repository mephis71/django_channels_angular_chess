from game.models import FreeBoardGame, Game

Game.objects.all().delete()
FreeBoardGame.objects.all().delete()
