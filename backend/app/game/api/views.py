from channels.layers import get_channel_layer
from game.api.serializers import FreeBoardGameSerializer, GameSerializer
from game.models import Game
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
        game_obj = request.user.freeboard_game
        if not game_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.serializer_class(game_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        settings = request.data['settings']
        serializer = self.serializer_class(data=settings)
        if serializer.is_valid(raise_exception=True):
            game_obj = serializer.save()
            request.user.freeboard_game = game_obj
            request.user.save(update_fields=['freeboard_game'])
            return Response(serializer.data, status=status.HTTP_200_OK)

        
 