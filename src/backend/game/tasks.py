from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
import asyncio
from rich import print
from .utils import to_timer_format, opposite_color
from .game_functions import end_game

def trigger_timer_task(game_obj):
    game_room_name = game_obj.get_game_name()
    task_name = f'{game_room_name}_timer'
    for task in asyncio.Task.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            asyncio.create_task(realtime_timer_broadcast(game_obj), name=task_name)
            return
    asyncio.create_task(realtime_timer_broadcast(game_obj), name=task_name)
    
async def realtime_timer_broadcast(game_obj):
    game_room_name = game_obj.get_game_name()
    turn = game_obj.get_turn()
    if turn == 'white':
        timer = game_obj.timer_white
    elif turn == 'black':
        timer = game_obj.timer_black
    else:
        try:
            raise Exception('Unindetified timer color')
        finally: 
            print('turn:', turn)
    while timer >= 0:
        timer -= 1
        msg = {
            'type': 'time',
            'time': to_timer_format(timer),
            'color': turn
        }
        await asyncio.sleep(1)
        if timer == 0:
            winner_color = opposite_color(turn)
            await end_game(game_obj, f'{winner_color}wins-oot')
            return
        await channel_layer.group_send(
            game_room_name,
            {
                'type': 'basic_broadcast',
                'text': msg
            }
        )

def cancel_timer_task(game_obj):
    game_room_name = game_obj.get_game_name()
    task_name = f'{game_room_name}_timer'
    for task in asyncio.Task.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return
    
def trigger_countdown_task(game_obj, username):
    game_room_name = game_obj.get_game_name()
    task_name = f'{game_room_name}_countdown_{username}'
    asyncio.create_task(endgame_countdown(game_obj, username), name=task_name)

async def endgame_countdown(game_obj, username):
    timer = 5
    while timer >= 0:
        timer -= 1
        await asyncio.sleep(1)
        if timer == 0:
            player_color = game_obj.get_color(username)
            game_result = f'{player_color}wins-abandonment'
            await end_game(game_obj, game_result)
    return

def cancel_countdown_task(game_obj, username):
    game_room_name = game_obj.get_game_name()
    task_name = f'{game_room_name}_countdown_{username}'
    for task in asyncio.Task.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return