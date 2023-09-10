from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from game.api.serializers import (
    CreateGameLiveSerializer,
    CreateGamePuzzleSerializer,
    RetrieveGameInProgressSerializer,
    RetrieveGameLiveSerializer,
    RetrieveGamePuzzleSerializer,
)
from game.models import GameInProgress, GameLive, GamePuzzle
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from game.misc import start_game

User = get_user_model()
channel_layer = get_channel_layer()


class StartGameAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        game_info = request.data["gameInfo"]
        start_game(game_info)
        return Response(status.HTTP_200_OK)
    

class GameInProgressViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveGameInProgressSerializer
    queryset = GameInProgress.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ...
        if self.action == "retrieve":
            return RetrieveGameInProgressSerializer


class GameLiveViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveGameLiveSerializer
    queryset = GameLive.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateGameLiveSerializer
        if self.action == "retrieve":
            return RetrieveGameLiveSerializer


class GamePuzzleViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveGamePuzzleSerializer
    queryset = GamePuzzle.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateGamePuzzleSerializer
        if self.action == "retrieve":
            return RetrieveGamePuzzleSerializer
