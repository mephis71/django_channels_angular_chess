from rich import print
from django.http import HttpResponse
from django.shortcuts import render
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
    player1 = request.GET.get('p1')
    player2 = request.GET.get('p2')

    game_obj = get_game(player1,player2)
    game_id = game_obj.id
    game_obj.is_running = True
    fen = game_obj.DEFAULT_GAME_FEN
    game_obj.init_game_with_fen(fen)

    
    msg = {
        'type': 'invite_accept',
        'player1': player1,
        'player2': player2,
        'game_id': game_id
    }

    async_to_sync(channel_layer.group_send)(
        "invite_group",
        {
            "type": "invite_broadcast",
            'text': msg
        })
    
    return HttpResponse('Invite accepted')

def endgame_handler(request):
    return

def get_game(username1,username2):
        return Game.objects.get_or_new(username1,username2)
