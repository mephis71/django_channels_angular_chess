import asyncio
from channels.db import database_sync_to_async
from utils.getters import get_friends_usernames
from .utils import broadcast_online_status

def start_disconnect_countdown(user):
    task_name = f'{user.username}_disconnect'
    asyncio.create_task(disconnect_countdown(user), name=task_name)

async def disconnect_countdown(user):
    seconds = 10
    while seconds >= 0:
        seconds -= 1
        await asyncio.sleep(1)
        if seconds == 0:
            user.is_online = False
            database_sync_to_async(user.save)()
            friends_usernames = await get_friends_usernames(user)
            await broadcast_online_status(user.username, 'offline', friends_usernames)

def cancel_disconnect_countdown(username):
    task_name = f'{username}_disconnect'
    for task in asyncio.tasks.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return

        