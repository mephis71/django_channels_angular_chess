from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

async def broadcast_online_status(username, status, friends_usernames):
        data = {
            'type': 'status',
            'username': username,
            'status': status
        }
        for friend_username in friends_usernames:
            await channel_layer.group_send(
                f'{friend_username}_system',
                {
                    'type': 'system_message',
                    'text': data
                }
            )