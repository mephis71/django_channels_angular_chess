from game.models import FreeBoardGame, GameLive

GameLive.objects.all().delete()
FreeBoardGame.objects.all().delete()
