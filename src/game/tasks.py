from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
import asyncio
from rich import print

def to_timer_format(seconds):
        s = seconds
        m = s//60
        s = s - m*60
        if m < 10:
            m = f'0{m}'
        if s < 10:
            s = f'0{s}'
        return f'{m}:{s}'

def trigger_timer_task(game_obj):
    channel_name = game_obj.get_game_name()
    for task in asyncio.Task.all_tasks():
        if task.get_name() == channel_name:
            task.cancel()
            asyncio.create_task(realtime_timer_broadcast(game_obj), name=channel_name)
            return
    asyncio.create_task(realtime_timer_broadcast(game_obj), name=channel_name)
    
async def realtime_timer_broadcast(game_obj):
    channel_name = game_obj.get_game_name()
    turn = game_obj.get_turn()
    timer = None
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
        await channel_layer.group_send(
            channel_name,
            {
                'type': 'basic_broadcast',
                'text': msg
            }
        )


