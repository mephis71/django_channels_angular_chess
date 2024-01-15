from django.urls import path
from rest_framework import routers

from .views import (
    GameInProgressViewSet,
    GameViewSet,
    GamePuzzleViewSet,
    StartGameAPIView,
)

router = routers.SimpleRouter()
router.register(r"puzzle", GamePuzzleViewSet)
router.register(r"live", GameViewSet)
router.register(r"game_in_progress", GameInProgressViewSet)

urlpatterns = [path("invite_accept/", StartGameAPIView.as_view())] + router.urls
