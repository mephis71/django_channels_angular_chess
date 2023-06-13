from channels.generic.websocket import AsyncJsonWebsocketConsumer
from utils.getters import get_user_with_jwt, get_user_with_pk, get_friends_usernames, get_friends_online_status
from channels.db import database_sync_to_async
from .utils import broadcast_online_status
from .tasks import start_disconnect_countdown, cancel_disconnect_countdown

class InviteConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope['cookies']['jwt']
        self.user = await get_user_with_jwt(token)
        
        await self.channel_layer.group_add(
            f'{self.user.username}_system',
            self.channel_name
        )

        await self.accept()

    async def receive_json(self, msg):
        to_user = msg['to_user']
        await self.channel_layer.group_send(
            f'{to_user}_system',
            {
                'type': 'system_message',
                'text': msg
            }
        )

    async def disconnect(self, close_code):
        pass
        # print('invite_close_code:', close_code)

    async def system_message(self, msg):
        msg = msg['text']
        await self.send_json(msg)

class OnlineStatusConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self.scope['cookies']['jwt']
        self.user = await get_user_with_jwt(token)

        await self.accept()

        cancel_disconnect_countdown(self.user.username)

        await self.channel_layer.group_add(
            f'{self.user.username}_system',
            self.channel_name
        )

        friends_online_status = await get_friends_online_status(self.user)
        data = {
            'type': 'friends_online_status',
            'friends_online_status': friends_online_status
        }

        await self.send_json(data)
        
    async def receive_json(self, msg):
        status = msg['status']
        
        user = await get_user_with_pk(self.user.pk)
        await self.set_online_status(user, status)

        friends_usernames = await get_friends_usernames(self.user)
        await broadcast_online_status(user.username, status, friends_usernames)

    async def disconnect(self, close_code):
        self.user = await get_user_with_pk(self.user.pk)
        start_disconnect_countdown(self.user)

    @database_sync_to_async
    def set_online_status(self, user, status):
        if status == 'online':
            user.is_online = True
        elif status == 'offline':
            user.is_online = False
        user.save()

    async def system_message(self, msg):
        msg = msg['text']
        await self.send_json(msg)
            