from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import unauthenticated_user
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, FriendRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def home_view(request, *args, **kwargs):
    return render(request, 'home.html')

@unauthenticated_user
def register_view(request, *args, **kwargs):
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home-page')
            
    context = {
        'form': form
    }
    return render(request, 'register.html', context)

@unauthenticated_user
def login_view(request, *args, **kwargs):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home-page')
        else: 
            messages.info(request, 'Username or password is incorrect')
            
    return render(request, 'login.html')

@login_required(login_url='login-page')
def user_view(request, username, *args, **kwargs):
    searched_user = CustomUser.objects.get(username=username)
    context = {
        'searched_user': searched_user,
    }
    return render(request, 'user.html', context)

@login_required(login_url='login-page')
def profile_settings_view(request, *args, **kwargs):
    form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form
    }
    return render(request, 'profile_settings.html', context)

@login_required(login_url='login-page')
def logout_view(request, *args, **kwargs):
    logout(request)
    return render(request, 'home.html')

@login_required(login_url='login-page')
def friends_view(request, *args, **kwargs):

    f_requests = FriendRequest.objects.filter(to_user_id = request.user.id)
    friends = request.user.friends

    context = {
        'f_requests': f_requests,
        'friends': friends
    }
    
    return render(request, 'friends.html', context)

@login_required(login_url='login-page')
def send_friend_request(request):
    to_user_username = request.POST.get('to_user_username')
    to_user = CustomUser.objects.get(username=to_user_username)
    to_user_id = to_user.id

    from_user_id = request.user.id
    from_user_username = request.user.username

    if from_user_username == to_user_username:
        msg = 'You can not invite yourself'
        context = {
            'msg': msg
        }
        return render(request, 'friends.html', context)

    f_request, status = FriendRequest.objects.get_or_create(
        to_user_id=to_user_id,
        to_user_username = to_user_username,
        from_user_id=from_user_id,
        from_user_username = from_user_username
        )

    if status == True:
        msg = 'Friend request sent'
    else:
        msg = 'Friend request already sent'

    context = {
        'msg': msg
    }

    return render(request, 'friends.html', context)

@login_required(login_url='login-page')
def accept_friend_request(request, request_id):
    f_request = FriendRequest.objects.get(id=request_id)
    from_user = CustomUser.objects.get(id=f_request.from_user_id)
    to_user = CustomUser.objects.get(id=f_request.to_user_id)
    from_user.friends.add(to_user)
    to_user.friends.add(from_user)
    f_request.delete()
    
    msg = 'Friend request from ' + from_user.username + ' accepted'

    context = {
        'msg': msg
    }

    return render(request, 'friends.html', context)

@login_required(login_url='login-page')
def remove_friend(request, friend_username):
    friend = CustomUser.objects.get(username=friend_username)
    request.user.friends.remove(friend)
    request.user.save()
    friend.friends.remove(request.user)
    friend.save()
    msg = f'Removed {friend_username} from friend list'
    context = {
        'msg': msg
    }
    return render(request, 'friends.html', context)
