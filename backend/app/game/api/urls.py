from django.urls import path
from rest_framework import routers

from .views import (
    GameInProgressViewSet,
    GameLiveViewSet,
    GamePuzzleViewSet,
    StartGameAPIView,
)

router = routers.SimpleRouter()
router.register(r"puzzle", GamePuzzleViewSet)
router.register(r"live", GameLiveViewSet)
router.register(r"game_in_progress", GameInProgressViewSet)

urlpatterns = [path("invite_accept/", StartGameAPIView.as_view())] + router.urls
