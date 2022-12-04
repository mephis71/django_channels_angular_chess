from .getters import get_game_by_id
from channels.db import database_sync_to_async
import asyncio
import datetime
from datetime import timezone
from .utils import endgame_JSON, move_JSON
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

async def end_game(game_obj, game_result):
    game_obj.is_running = False
    game_obj.is_finished = True
    game_room_name = game_obj.get_game_name()
    if game_result in ('whitewins-abandonment' or 'blackwins-abandonment'):
        for task in asyncio.Task.all_tasks():
            if task.get_name() == f'{game_room_name}_timer':
                task.cancel()
        if game_result == 'blackwins-abandonment':
            game_obj.winner = game_obj.player_black
        elif game_result == 'whitewins-abandonment':
            game_obj.winner = game_obj.player_white
        game_obj.endgame_cause = 'ABANDONMENT'
    if game_result == 'whitewins-oot':
        game_obj.winner = game_obj.player_white
        game_obj.timer_black = 0
        game_obj.endgame_cause = 'OUT OF TIME'
    if game_result == 'blackwins-oot':
        game_obj.winner = game_obj.player_black
        game_obj.timer_white = 0
        game_obj.endgame_cause = 'OUT OF TIME'
    if game_result == 'whitewins':
        game_obj.winner = game_obj.player_white
        game_obj.endgame_cause = 'CHECKMATE'
    elif game_result == 'blackwins':
        game_obj.winner = game_obj.player_black
        game_obj.endgame_cause = 'CHECKMATE'
    elif game_result == 'draw-stalemate':
        game_obj.endgame_cause = 'STALEMATE'
    elif game_result == 'draw-3r':
        game_obj.endgame_cause = 'THREEFOLD REPETITION'
    elif game_result == 'draw-50m':
        game_obj.endgame_cause = '50 MOVES RULE'
    elif game_result == 'draw-mutual':
        for task in asyncio.Task.all_tasks():
            if task.get_name() == f'{game_room_name}_timer':
                task.cancel()
        now = datetime.datetime.now(tz=timezone.utc)
        time_dif = now - game_obj.last_move_time
        time_dif_seconds = int(time_dif.seconds)
        if game_obj.get_turn() == 'white':
            game_obj.timer_white -= time_dif_seconds
        elif game_obj.get_turn() == 'black':
            game_obj.timer_black -= time_dif_seconds
        game_obj.endgame_cause = 'MUTUAL AGREEMENT'
    game_obj.game_end_time = datetime.datetime.now(tz=timezone.utc)
    await database_sync_to_async(game_obj.save)()
    await database_sync_to_async(game_obj.add_to_history)()
    msg = endgame_JSON(game_obj, game_result)
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': msg
        }
    )
    return

async def update_game(game_obj, new_fen):
    turn = game_obj.get_turn()

    if game_obj.is_running == False:
        game_obj.is_running = True
        now = datetime.datetime.now(tz=timezone.utc)
        game_obj.game_start_time = now
        game_obj.last_move_time = now
    else:
        now = datetime.datetime.now(tz=timezone.utc)
        time_dif = now - game_obj.last_move_time
        time_dif_seconds = int(time_dif.seconds)
        if turn == 'white':
            game_obj.timer_white -= time_dif_seconds
        elif turn == 'black':
            game_obj.timer_black -= time_dif_seconds
        game_obj.last_move_time = now

    game_obj.fen = new_fen
    game_obj.game_positions += ';' + new_fen
    game_obj.move_timestamps += f';{game_obj.timer_white}-{game_obj.timer_black}'

    await database_sync_to_async(game_obj.save)()
    return game_obj

async def end_move(game_obj):
    data = move_JSON(game_obj)
    game_room_name = game_obj.get_game_name()
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': data
        }
    )
    return

async def send_draw_offer(game_obj, channel_name):
    game_room_name = game_obj.get_game_name()
    data = {
        'type': 'draw_offer',
        'sender_channel_name': channel_name
    }
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'draw_offer_broadcast',
            'text': data
        }
    )

async def reject_draw_offer(game_obj):
    game_room_name = game_obj.get_game_name()
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': {
                'type': 'draw_reject',
            }
        }
    )