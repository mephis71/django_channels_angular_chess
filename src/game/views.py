from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


def game_view(request, *args, **kwargs):
    return render(request, 'game.html',{})
