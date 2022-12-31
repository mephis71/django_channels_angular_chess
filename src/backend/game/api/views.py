from rest_framework.response import Response
from rest_framework import status
from game.models import Game
from game.api.serializers import GameSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from asgiref.sync import async_to_sync
from rich import print
from game.getters import new_game

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
        game_obj.save()

        msg = {
            'type': 'invite_accept',
            'usernames': usernames,
            'game_id': game_id
        }

        async_to_sync(channel_layer.group_send)(
            "invite_group",
            {
                "type": "basic_broadcast",
                'text': msg
            }
        )

        return Response(status=status.HTTP_202_ACCEPTED)
