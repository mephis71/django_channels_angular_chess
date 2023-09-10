from django.contrib import admin
from game.models import GameLive


class GameLiveAdmin(admin.ModelAdmin):
    model = GameLive


admin.site.register(GameLive, GameLiveAdmin)
