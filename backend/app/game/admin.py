from django.contrib import admin
from game.models import Game


class GameAdmin(admin.ModelAdmin):
    model = Game


admin.site.register(Game, GameAdmin)
