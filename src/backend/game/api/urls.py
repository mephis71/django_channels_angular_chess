from django.urls import path

from .views import *

urlpatterns = [
    path('<int:id>/', GameAPIView.as_view()),
    path('invite_accept/', GameInviteAcceptAPIView.as_view()),
] 