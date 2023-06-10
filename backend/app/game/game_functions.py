import asyncio
import datetime
from datetime import timezone

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from utils.getters import new_game

from .utils import endgame_JSON, move_cancel_JSON, move_JSON

channel_layer = get_channel_layer()

async def end_game(game_obj, game_result):
    game_room_name = game_obj.get_game_name()
    now = datetime.datetime.now(tz=timezone.utc)

    if game_result not in ('whitewins-oot', 'blackwins-oot'):
        for task in asyncio.all_tasks():
            if task.get_name() == f'{game_room_name}_timer':
                task.cancel()

    if game_result in ('whitewins-abandonment', 'blackwins-abandonment'):
        if game_obj.is_running:
            time_dif = now - game_obj.last_move_time
            time_dif_seconds = int(time_dif.seconds)
            if game_obj.get_turn() == 'white':
                game_obj.timer_white -= time_dif_seconds
            elif game_obj.get_turn() == 'black':
                game_obj.timer_black -= time_dif_seconds
            move_timestamps = game_obj.move_timestamps.split(';')
            move_timestamps[-1] = f'{game_obj.timer_white}-{game_obj.timer_black}'
            game_obj.move_timestamps = ";".join(move_timestamps)

            if game_result == 'blackwins-abandonment':
                game_obj.winner = game_obj.player_black
            elif game_result == 'whitewins-abandonment':
                game_obj.winner = game_obj.player_white
            game_obj.endgame_cause = 'ABANDONMENT'
        else:
            game_obj.endgame_cause = 'DRAW (ABANDONED)'
            game_result = 'draw-abandonment'

    elif game_result == 'whitewins-oot':
        game_obj.winner = game_obj.player_white
        game_obj.timer_black = 0
        game_obj.endgame_cause = 'OUT OF TIME'

    elif game_result == 'blackwins-oot':
        game_obj.winner = game_obj.player_black
        game_obj.timer_white = 0
        game_obj.endgame_cause = 'OUT OF TIME'

    elif game_result == 'whitewins':
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
        if game_obj.is_running:
            time_dif = now - game_obj.last_move_time
            time_dif_seconds = int(time_dif.seconds)
            if game_obj.get_turn() == 'white':
                game_obj.timer_white -= time_dif_seconds
            elif game_obj.get_turn() == 'black':
                game_obj.timer_black -= time_dif_seconds
            move_timestamps = game_obj.move_timestamps.split(';')
            move_timestamps[-1] = f'{game_obj.timer_white}-{game_obj.timer_black}'
            game_obj.move_timestamps = ";".join(move_timestamps)
        game_obj.endgame_cause = 'MUTUAL AGREEMENT'
    
    elif game_result in ('whitewins-resignment', 'blackwins-resignment'):
        if game_obj.is_running:
            time_dif = now - game_obj.last_move_time
            time_dif_seconds = int(time_dif.seconds)
            if game_obj.get_turn() == 'white':
                game_obj.timer_white -= time_dif_seconds
            elif game_obj.get_turn() == 'black':
                game_obj.timer_black -= time_dif_seconds
            move_timestamps = game_obj.move_timestamps.split(';')
            move_timestamps[-1] = f'{game_obj.timer_white}-{game_obj.timer_black}'
            game_obj.move_timestamps = ";".join(move_timestamps)
            game_obj.endgame_cause = 'RESIGNMENT'
            if game_result == 'whitewins-resignment':
                game_obj.winner = game_obj.player_white
            elif game_result == 'blackwins-resignment':
                game_obj.winner = game_obj.player_black
        else:
            game_obj.endgame_cause = 'DRAW (ABANDONED)'
            game_result = 'draw-abandonment'
    
    game_obj.game_end_time = now
    game_obj.is_running = False
    game_obj.is_finished = True
    game_obj._game_result = game_result

    await database_sync_to_async(game_obj.save)()
    await database_sync_to_async(game_obj.add_to_history)()

    msg = endgame_JSON(game_obj)
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': msg
        }
    )

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

async def end_freeboard_game(game_obj, game_result):
    if game_result == 'whitewins':
        game_obj.endgame_cause = 'CHECKMATE'

    elif game_result == 'blackwins':
        game_obj.endgame_cause = 'CHECKMATE'

    elif game_result == 'draw-stalemate':
        game_obj.endgame_cause = 'STALEMATE'

    elif game_result == 'draw-3r':
        game_obj.endgame_cause = 'THREEFOLD REPETITION'

    elif game_result == 'draw-50m':
        game_obj.endgame_cause = '50 MOVES RULE'

    game_obj._game_result = game_result

    await database_sync_to_async(game_obj.save)()

async def update_freeboard_game(game_obj, new_fen):
    game_obj.fen = new_fen
    game_obj.game_positions += ';' + new_fen

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

async def send_draw_offer(game_obj, channel_name):
    game_room_name = game_obj.get_game_name()
    data = {
        'type': 'draw_offer',
        'sender_channel_name': channel_name
    }
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'one_way_broadcast',
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

async def send_move_cancel_request(game_obj, channel_name, username):
    game_room_name = game_obj.get_game_name()
    sender_color = game_obj.get_color(username)
    game_positions = game_obj.get_game_positions()
    
    try:
        if sender_color == game_obj.get_turn():
            fen = game_positions[-3]
        else:
            fen = game_positions[-2]
    except IndexError:
        raise

    data = {
        'type': 'move_cancel_request',
        'sender_channel_name': channel_name
    }
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'one_way_broadcast',
            'text': data
        }
    )

    game_obj._move_cancel_fen = fen
    await database_sync_to_async(game_obj.save)()

async def reject_move_cancel_request(game_obj):
    game_room_name = game_obj.get_game_name()
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': {
                'type': 'move_cancel_reject',
            }
        }
    )

async def accept_move_cancel_request(game_obj):
    game_positions = game_obj.get_game_positions()
    move_timestamps = game_obj.get_raw_move_timestamps()

    index = game_positions.index(game_obj._move_cancel_fen)
    game_positions = game_positions[:(index + 1)]
    move_timestamps = move_timestamps[:(index + 1)]

    timers = move_timestamps[-1].split('-')
    game_obj.timer_white = int(timers[0])
    game_obj.timer_black = int(timers[1])

    game_obj.move_timestamps = ";".join(move_timestamps)
    game_obj.game_positions = ";".join(game_positions)
    game_obj.fen = game_obj._move_cancel_fen
    game_obj.last_move_time = datetime.datetime.now(tz=timezone.utc)
    game_obj._move_cancel_fen = None

    await database_sync_to_async(game_obj.save)()

    game_room_name = game_obj.get_game_name()
    data = move_cancel_JSON(game_obj)
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': data
        }
    )

    return game_obj

async def send_rematch(game_obj, channel_name):
    game_room_name = game_obj.get_game_name()
    data = {
        'type': 'rematch',
        'sender_channel_name': channel_name
    }
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'one_way_broadcast',
            'text': data
        }
    )

async def reject_rematch(game_obj, channel_name):
    game_room_name = game_obj.get_game_name()
    data = {
        'type': 'rematch_reject',
        'sender_channel_name': channel_name
    }
    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'one_way_broadcast',
            'text': data
        }
    )

async def accept_rematch(game_obj):
    game_room_name = game_obj.get_game_name()
    
    usernames = (game_obj.player_white.username, game_obj.player_black.username)
    settings = {
        "white": game_obj.player_white.username,
        "black": game_obj.player_black.username,
        "random_colors": game_obj.random_colors,
        "duration": game_obj.duration
    }

    game_obj = await database_sync_to_async(new_game)(usernames, settings)
    game_id = game_obj.id
    await database_sync_to_async(game_obj.save)()

    data = {
        'type': 'rematch_accept',
        'game_id': game_id
    }

    await channel_layer.group_send(
        game_room_name,
        {
            'type': 'basic_broadcast',
            'text': data
        }
    )

