import asyncio

from async_getters import get_friends_usernames
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


async def broadcast_online_status(user_id, status, friends_ids):
    data = {"type": "status", "user_id": user_id, "status": status}
    for friend_id in friends_ids:
        await channel_layer.group_send(
            f"{friend_id}_system", {"type": "system_message", "text": data}
        )


def start_disconnect_countdown(user):
    task_name = f"{user.username}_disconnect"
    asyncio.create_task(disconnect_countdown(user), name=task_name)


async def disconnect_countdown(user):
    seconds = 10
    while seconds >= 0:
        seconds -= 1
        await asyncio.sleep(1)
        if seconds == 0:
            user.is_online = False
            await database_sync_to_async(user.save)(update_fields=["is_online"])
            friends_usernames = await get_friends_usernames(user)
            await broadcast_online_status(user.id, "offline", friends_usernames)


def cancel_disconnect_countdown(username):
    task_name = f"{username}_disconnect"
    for task in asyncio.tasks.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return
