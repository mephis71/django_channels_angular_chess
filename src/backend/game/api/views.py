from rest_framework.response import Response
from rest_framework import status
from game.models import Game
from game.api.serializers import GameSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated



class GameAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GameSerializer

    def get(self, request, *args, **kwargs):
        game_id = kwargs['id']
        try:
            game_obj = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(game_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


