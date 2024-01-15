from channels.generic.websocket import AsyncJsonWebsocketConsumer

"""User system channel name is {user_id}_system."""


class MyAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    async def send_system_message(self, user_id: int, msg: dict) -> None:
        """
        Send system message to a user by his id.
        """
        await self.channel_layer.group_send(
                f"{user_id}_system", {"type": "system_message", "text": msg}
            )