from channels.consumer import AsyncConsumer
import json
from .models import Game
from rich import print
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


class GameConsumer(AsyncConsumer):

    async def websocket_connect(self, event):

        # accept the connection
        await self.send({
            'type': 'websocket.accept',
        })

        # grab both users and the game related to those users
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        self.game_obj = await self.get_game(me,other_user)
        database_sync_to_async(self.game_obj.refresh_from_db)()

        # grab the name of the 'game room' and assigning it to the class
        game_room_name = self.game_obj.get_game_name()
        self.game_room_name = game_room_name

        # add the player (consumer) to the 'game room' (game_room_name)
        await self.channel_layer.group_add(
            game_room_name,
            self.channel_name 
        )

        # add the user to the list of connected players in model
        await self.add_player(me)

        # grab the game state
        game_state = await self.get_game_state()

        # data contains color of the player and fen of the game, turn and type of 'init' 
        data = await self.init_JSON(game_state, me)

        # send the state of the game to the player which then updates the game on his side
        await self.send({
            'type': 'websocket.send',
            'text': data
        })
                
    async def websocket_receive(self,event):
        # grab both users and the game related to those users
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        self.game_obj = await self.get_game(me,other_user)

        # decode from JSON
        msg = event['text']
        msg = json.loads(msg)

        # check if the message is a 'move' or 'endgame' type
        type = msg['type']

        if type == 'move':

            fen = msg['fen']
            # save the position of the game sent by player to the model
            await self.move_handler(fen)

            # grab the game state
            game_state = await self.get_game_state()

            # pack the data to JSON and python dict
            dict = await self.move_JSON(game_state)
            
            # send the move (new state of the game) to the other player (actually to both [group of self.game_room_name] but that doesnt make a difference)
            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type':'move_broadcast',
                    'text': dict
                }
            )
        
        if type == 'endgame':

            fen = msg['fen']
            result = msg['result']

            await self.move_handler(fen)

            dict = await self.endgame_JSON(fen, result)

            await self.channel_layer.group_send(
                self.game_room_name,
                {
                    'type': 'endgame_broadcast',
                    'text': dict
                }
            )

            
    # handler for sending the position of the game to both players using group
    async def move_broadcast(self, event):
        data = event['text']['data']
        jsonObj = event['text']['jsonObj']

        await self.update_game(data)

        await self.send({
            "type": 'websocket.send',
            'text': jsonObj
        })
    

    async def endgame_broadcast(self, event):
        data = event['text']['data']
        jsonObj = event['text']['jsonObj']

        await self.update_endgame(data)
        
        await self.send({ 
            'type': 'websocket.send',
            'text': jsonObj
        })

    async def websocket_disconnect(self, event):
        
        # remove the user from the list of connected players in model
        me = self.scope['user']
        await self.remove_player(me)

        # remove consumer from the group
        await self.channel_layer.group_discard(
            self.game_room_name,
            self.channel_name
        )

        # disconnect
        await self.send({
            'type': 'websocket.disconnect'
        })
        
    @database_sync_to_async
    def move_handler(self, msg):
        obj = self.game_obj
        obj.game_state = msg
        if obj.turn == 'white':
            obj.turn = 'black'
        else:
            obj.turn = 'white'
        obj.save()

    @database_sync_to_async
    def update_game(self,data):
        fen = data['fen']
        turn = data['turn']
        obj = self.game_obj
        obj.game_state = fen
        obj.turn = turn
        obj.save()

    @database_sync_to_async
    def update_endgame(self, data):
        fen = data['fen']
        obj = self.game_obj
        obj.game_state = fen
        obj.save()


    @database_sync_to_async
    def get_game(self,username1,username2):
        return Game.objects.get_or_new(username1,username2)
    
    @database_sync_to_async
    def get_game_state(self):
        return self.game_obj.game_state
    
    @database_sync_to_async
    def get_turn(self):
        return self.game_obj.turn

    @database_sync_to_async
    def add_player(self, username):
        self.game_obj.add_player(username)

    @database_sync_to_async
    def remove_player(self, username):
        self.game_obj.remove_player(username)

    @database_sync_to_async
    def move_JSON(self, value):
        turn = self.game_obj.turn
        data = {
            'type': 'move',
            'fen': value,
            'turn': turn
        }
        jsonObj = json.dumps(data)
        dict = {
            'jsonObj': jsonObj,
            'data': data
        }
        return dict
    
    @database_sync_to_async
    def init_JSON(self, fen, user):
        turn = self.game_obj.turn
        color = self.game_obj.get_color(user)
        jsonObj = {
            'type': 'init',
            'fen': fen,
            'color': color,
            'turn': turn
        }
        
        jsonObj = json.dumps(jsonObj)

        return jsonObj

    @database_sync_to_async
    def endgame_JSON(self, fen, result):
        data = {
            'type': 'endgame',
            'fen': fen,
            'result': result
        }

        jsonObj = json.dumps(data)

        dict = {
            'data': data,
            'jsonObj': jsonObj
        }

        return dict
