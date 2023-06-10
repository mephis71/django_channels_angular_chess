from django.urls import path

from .views import *

urlpatterns = [
    path('', UserRetrieveUpdateAPIView.as_view()),
    path('profile/<str:username>', UserProfileAPIView.as_view()),
    path('register/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('send_friend_request/', SendFriendRequestAPIView.as_view()),
    path('accept_friend_request/<int:id>', AcceptFriendRequestAPIView.as_view()),
    path('reject_friend_request/<int:id>', RejectFriendRequestAPIView.as_view()),
    path('running_games', UserRunningGamesAPIView.as_view()),
    path('remove_friend/<str:friend_username>', RemoveFriendAPIView.as_view()),
] 