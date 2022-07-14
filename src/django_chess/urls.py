from django.contrib import admin
from django.urls import path
from game.views import game_view, game_view_against
from users.views import profile_settings_view, user_view, friends_view, send_friend_request, accept_friend_request, home_view, logout_view, register_view, login_view

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home-page'),
    path('login/',login_view, name='login-page'),
    path('register/',register_view, name='register-page'),
    path('logout/', logout_view, name='logout-page'),
    path('settings/', profile_settings_view, name='profile-settings-page'),
    
    path('game/',game_view,name='game-page'),
    path('game/<str:username>',game_view_against,name='game-against-page'),

    path('friends/', friends_view, name='friends-page'),
    path('send_friend_request/', send_friend_request, name='send-friend-request'),
    path('accept_friend_request/<int:request_id>/', accept_friend_request, name='accept-friend-request'),
    path('<str:username>/',user_view, name='user-page'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
