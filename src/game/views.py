from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from rich import print
from .models import Game

def game_view(request, *args, **kwargs):
    friends = request.user.friends
    context = {
        'friends': friends,
    }
    return render(request, 'game.html', context)

def game_view_against(request, username, *args, **kwargs):
    return render(request,'game_against.html')

def get_game(username1,username2):
        return Game.objects.get_or_new(username1,username2)