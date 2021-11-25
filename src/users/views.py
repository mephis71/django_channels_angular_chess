from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from pages.forms import ProfileForm
from rich import print

# Create your views here.

@login_required(login_url='login')
def user_view(request, *args, **kwargs):

    name = request.user.profile.name
    username = request.user.get_username()
    profile_pic = request.user.profile.profile_pic
    
    context = {
        'name': name,
        'username': username,
        'profile_pic': profile_pic,
        'user': request.user,
    }
    return render(request, 'user.html', context)


@login_required(login_url='login')
def profile_settings_view(request, *args, **kwargs):
    
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user-page')
           


    context = {
        'form':form,
    }
    return render(request,'profile_settings.html', context)
