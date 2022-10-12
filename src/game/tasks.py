from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
import asyncio

from channels.db import database_sync_to_async
from rich import print

from .models import Game


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
        if timer == 0:
            await end_game(game_id=game_obj.id, turn=turn, channel_name=channel_name)
            return
        await channel_layer.group_send(
            channel_name,
            {
                'type': 'basic_broadcast',
                'text': msg
            }
        )

async def end_game(game_id, turn, channel_name):
    game_obj = await get_game_by_id(game_id)
    game_obj.is_running = False
    game_obj.is_finished = True
    if turn == 'white':
        game_result = 'blackwins-oot'
        game_obj.winner = game_obj.player_black
        game_obj.timer_white = 0 
    elif turn == 'black':
        game_result = 'whitewins-oot'
        game_obj.winner = game_obj.player_white
        game_obj.timer_black = 0
    game_obj.endgame_cause = 'OUT OF TIME'
    await database_sync_to_async(game_obj.save)()
    msg = endgame_JSON(game_obj, game_result)
    await channel_layer.group_send(
        channel_name,
        {
            'type': 'basic_broadcast',
            'text': msg
        }
    )
    return

@database_sync_to_async
def get_game_by_id(game_id):
    return Game.objects.select_related("player_white", "player_black").get(id=game_id)

def endgame_JSON(game_obj, game_result):
    fen = game_obj.fen
    turn = game_obj.get_turn()
    time_black = to_timer_format(game_obj.timer_black)
    time_white = to_timer_format(game_obj.timer_white)
    moves_list = game_obj.get_moves_list()
    data = {
        'type': 'endgame',
        'fen': fen,
        'turn': turn,
        'time_black': time_black,
        'time_white': time_white,
        'game_result': game_result,
        'moves_list': moves_list
    }
    return data
