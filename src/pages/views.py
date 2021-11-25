from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from .forms import CreateUserForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import Profile
# Create your views here.



def home_view(request, *args, **kwargs):
    return render(request, 'home.html', {})

@unauthenticated_user
def login_view(request, *args, **kwargs):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            messages.info(request, 'Username or password is incorrect')
            
    context = {

    }
    return render(request, 'login.html', context)

@unauthenticated_user
def register_view(request, *args, **kwargs):

    register_form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user = user,
                name = 'initialname'
            )
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            
            return redirect('login')

    context = {
        'form': register_form
    }

    return render(request, 'register.html', context)

@login_required(login_url='login')
def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('login')
