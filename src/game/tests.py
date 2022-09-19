from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase

from django_chess.asgi import application
from .views import get_game
from rich import print
from .consumers import GameConsumer

User = get_user_model()

class WhiteWinsTest(TestCase):
    def setUp(self):
        username_1 = 'test1'
        username_2 = 'test2'
        self.user_1 = User.objects.create(username=username_1)
        self.user_2 = User.objects.create(username=username_2)
        self.game_obj = get_game(username_1, username_2)
        self.game_obj.assign_colors_randomly(username_1, username_2)
        self.game_id = self.game_obj.id
        self.game_obj.is_running = True
        self.game_obj.save()
        
    async def test_game_consumer(self):
        communicator_1 = WebsocketCommunicator(
            application=application,
            path=f'/game/live/{self.game_id}/'
            )
        communicator_2 = WebsocketCommunicator(
            application=application,
            path=f'/game/live/{self.game_id}/'
            )  
        communicator_1.scope['user'] = self.user_1
        communicator_2.scope['user'] = self.user_2

        connected1, _ = await communicator_1.connect()
        connected2, _ = await communicator_2.connect()
        self.assertEqual(connected1, True)
        self.assertEqual(connected2, True)
        response_1 = await communicator_1.receive_json_from()
        response_2 = await communicator_2.receive_json_from()

        moves_white = ((52,36), (59,45), (61,34), (34,27), (45,13))
        moves_black = ((11,27), (8,16), (9,17), (2,11))
        
        for i in range(len(moves_white)):
            await communicator_1.send_json_to({  
                'color': 'white',
                'type': "move",
                'picked_id': moves_white[i][0],
                'target_id': moves_white[i][1],
            })

            response_1 = await communicator_1.receive_json_from()
            response_2 = await communicator_2.receive_json_from()
            await communicator_1.receive_nothing()
            await communicator_2.receive_nothing()

            if i == len(moves_white) - 1 and (len(moves_white) > len(moves_black)):
                break

            await communicator_2.send_json_to({  
                'color': 'black',
                'type': "move",
                'picked_id': moves_black[i][0],
                'target_id': moves_black[i][1],
            })

            response_1 = await communicator_1.receive_json_from()
            response_2 = await communicator_2.receive_json_from()
            await communicator_1.receive_nothing()
            await communicator_2.receive_nothing()

        game_obj = await GameConsumer.get_game_by_id(self.game_id)
        self.assertEqual(game_obj.player_white_id, game_obj.winner_id)

class BlackWinsTest(TestCase):
    def setUp(self):
        username_1 = 'test3'
        username_2 = 'test4'
        self.user_1 = User.objects.create(username=username_1)
        self.user_2 = User.objects.create(username=username_2)
        self.game_obj = get_game(username_1, username_2)
        self.game_obj.assign_colors_randomly(username_1, username_2)
        self.game_id = self.game_obj.id
        self.game_obj.is_running = True
        self.game_obj.save()
        
    async def test_game_consumer(self):
        communicator_1 = WebsocketCommunicator(
            application=application,
            path=f'/game/live/{self.game_id}/'
            )
        communicator_2 = WebsocketCommunicator(
            application=application,
            path=f'/game/live/{self.game_id}/'
            )  
        communicator_1.scope['user'] = self.user_1
        communicator_2.scope['user'] = self.user_2

        connected1, _ = await communicator_1.connect()
        connected2, _ = await communicator_2.connect()
        self.assertEqual(connected1, True)
        self.assertEqual(connected2, True)
        response_1 = await communicator_1.receive_json_from()
        response_2 = await communicator_2.receive_json_from()

        moves_white = ((52,36), (61,52), (57,40), (49,41), (40,25))
        moves_black = ((11,27), (12,20), (3,21), (5,26), (21, 53))
        
        for i in range(len(moves_white)):
            await communicator_1.send_json_to({  
                'color': 'white',
                'type': "move",
                'picked_id': moves_white[i][0],
                'target_id': moves_white[i][1],
            })

            response_1 = await communicator_1.receive_json_from()
            response_2 = await communicator_2.receive_json_from()
            await communicator_1.receive_nothing()
            await communicator_2.receive_nothing()

            if i == len(moves_white) - 1 and (len(moves_white) > len(moves_black)):
                break

            await communicator_2.send_json_to({  
                'color': 'black',
                'type': "move",
                'picked_id': moves_black[i][0],
                'target_id': moves_black[i][1],
            })

            response_1 = await communicator_1.receive_json_from()
            response_2 = await communicator_2.receive_json_from()
            await communicator_1.receive_nothing()
            await communicator_2.receive_nothing()

        game_obj = await GameConsumer.get_game_by_id(self.game_id)
        self.assertEqual(game_obj.player_black_id, game_obj.winner_id)
        
        
        

      