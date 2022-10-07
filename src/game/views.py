from rich import print
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Game
import json

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

from asgiref.sync import async_to_sync

def game_view(request, *args, **kwargs):
    friends = request.user.friends
    context = {
        'friends': friends,
    }
    return render(request, 'game.html', context)

def game_view_against(request, username, *args, **kwargs):
    return render(request,'game_against.html')

def game_live_view(request, game_id, *args, **kwargs):
    return render(request,'game_against.html')

def game_invite_handler(request):
    username1 = request.GET.get('p1')
    username2 = request.GET.get('p2')

    game_obj = get_game(username1, username2)
    game_obj.assign_colors_randomly(username1, username2)
    game_id = game_obj.id
    game_obj.save()
    msg = {
        'type': 'invite_accept',
        'player1': username1,
        'player2': username2,
        'game_id': game_id
    }

    async_to_sync(channel_layer.group_send)(
        "invite_group",
        {
            "type": "invite_accept_broadcast",
            'text': msg
        }
    )
    
    return HttpResponse('Invite accepted')

def get_game(username1,username2):
        return Game.objects.get_or_new(username1,username2)
