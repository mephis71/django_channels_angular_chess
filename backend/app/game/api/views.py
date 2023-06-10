from channels.layers import get_channel_layer
from game.api.serializers import FreeBoardGameSerializer, GameSerializer, FreeBoardGameCreateSerializer
from game.models import Game, FreeBoardGame
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

channel_layer = get_channel_layer()
from asgiref.sync import async_to_sync
from utils.getters import new_game

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

class GameInviteAcceptAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        invite = request.data['invite']
        usernames = (invite['from_user'], invite['to_user'])
        settings = invite['settings']
        
        game_obj = new_game(usernames, settings)
        game_id = game_obj.id

        msg = {
            'type': 'game_invite_accept',
            'usernames': usernames,
            'game_id': game_id
        }

        for username in usernames:
            async_to_sync(channel_layer.group_send)(
            f"{username}_system",
            {
                "type": "system_message",
                'text': msg
            }
        )

        return Response(status=status.HTTP_202_ACCEPTED)
    
class GameFreeBoardAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FreeBoardGameSerializer

    def get(self, request, *args, **kwargs):
        game_id = kwargs['id']
        try:
            game_obj = FreeBoardGame.objects.get(id=game_id)
        except FreeBoardGame.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(game_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        settings = request.data['settings']
        serializer = FreeBoardGameCreateSerializer(data=settings)
        if serializer.is_valid():
            game_obj = serializer.save()   
            serializer = self.serializer_class(game_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
