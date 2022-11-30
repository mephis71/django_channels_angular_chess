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
        print('test')
        player1 = request.data['invite_accept']['p1']
        player2 = request.data['invite_accept']['p2']
        game_obj = get_game(player1, player2)
        game_obj.assign_colors_randomly(player1, player2)
        game_id = game_obj.id
        game_obj.save()

        msg = {
            'type': 'invite_accept',
            'player1': player1,
            'player2': player2,
            'game_id': game_id
        }

        async_to_sync(channel_layer.group_send)(
            "invite_group",
            {
                "type": "invite_accept_broadcast",
                'text': msg
            }
        )

        return Response(status=status.HTTP_202_ACCEPTED)

def get_game(username1, username2):
    return Game.objects.get_or_new(username1, username2)
