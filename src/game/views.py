from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from users.models import Profile
from rich import print

def game_view(request, *args, **kwargs):

    current_user = request.user
    profiles = Profile.objects.exclude(user = current_user)
    context = {
        'profiles': profiles,
    }
    return render(request, 'game.html', context)

def game_view_against(request, *args, **kwargs):
    
     
    return render(request,'game_against.html',{})
