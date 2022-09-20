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
        self.assertEqual(game_obj.endgame_cause, 'CHECKMATE')
        self.assertEqual(game_obj.is_finished, True)
        self.assertEqual(game_obj.is_running, False)

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
        self.assertEqual(game_obj.endgame_cause, 'CHECKMATE')
        self.assertEqual(game_obj.is_finished, True)
        self.assertEqual(game_obj.is_running, False)

class ThreefoldRepetitionTest(TestCase):
    def setUp(self):
        username_1 = 'test5'
        username_2 = 'test6'
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

        moves_white = ((52,36), (62,45), (61,52), (52,61), (61,52), (52,61))
        moves_black = ((11,27), (6,21), (3,11), (11,3), (3, 11), (11,3))
        
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
        self.assertEqual(game_obj.winner_id, None)
        self.assertEqual(game_obj.endgame_cause, 'THREEFOLD REPETITION')
        self.assertEqual(game_obj.is_finished, True)
        self.assertEqual(game_obj.is_running, False)

class FiftyMovesRuleTest(TestCase):
    def setUp(self):
        username_1 = 'test7'
        username_2 = 'test8'
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

        moves_white = ((52, 44), (61, 52), (52, 45), (45, 36), (36, 43), (43, 34), (34, 41), (41, 32), (59, 52), (52, 43), (43, 36), (36, 35), (35, 34), (34, 33), (57, 42), (62, 52), (60, 62), (33, 41), (41, 40), (42, 25), (40, 41), (41, 42), (42, 43), (43, 35), (35, 34)) 
        moves_black = ((12, 20), (5, 12), (12, 21), (21, 28), (28, 19), (19, 26), (26, 17), (17, 24), (3, 12), (12, 19), (19, 28), (28, 27), (27, 26), (26, 25), (1, 18), (6, 12), (4, 6), (25, 17), (17, 16), (18, 33), (16, 17), (17, 18), (18, 19), (19, 27), (27, 26))
        
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
        self.assertEqual(game_obj.winner_id, None)
        self.assertEqual(game_obj.endgame_cause, '50 MOVES RULE')
        self.assertEqual(game_obj.is_finished, True)
        self.assertEqual(game_obj.is_running, False)

class StalemateTest(TestCase):
    def setUp(self):
        username_1 = 'test9'
        username_2 = 'test10'
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

        moves_white = ((52, 36), (36, 27), (27, 20), (59, 52), (52, 16), (16, 8), (8, 0), (0, 1), (1, 9), (9, 10), (10, 14), (14, 7), (7, 15), (15, 6), (6, 20), (60, 59), (58, 40), (59, 50), (40, 33), (50, 41), (33, 19), (41, 49), (49, 41), (41, 49), (49, 41), (41, 49), (49, 41), (41, 49), (49, 57), (57, 56)) 
        moves_black = ((11, 27), (12, 20), (13, 20), (3, 21), (21, 49), (49, 48), (48, 56), (56, 57), (57, 50), (50, 22), (22, 54), (54, 63), (63, 55), (55, 62), (2, 20), (5, 40), (62, 61), (61, 53), (20, 41), (53, 51), (51, 19), (4, 12), (12, 20), (20, 28), (28, 36), (36, 43), (19, 26), (26, 27), (43, 51), (51, 50))
        
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
        self.assertEqual(game_obj.winner_id, None)
        self.assertEqual(game_obj.endgame_cause, 'STALEMATE')
        self.assertEqual(game_obj.is_finished, True)
        self.assertEqual(game_obj.is_running, False)
        
        
        

      