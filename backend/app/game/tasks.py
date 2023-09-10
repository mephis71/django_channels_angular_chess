import asyncio

from channels.layers import get_channel_layer
from game.game_engine.game_cls import Color, GameResult
from game.game_engine.game_funcs import opposite_color, seconds_to_timer_format

channel_layer = get_channel_layer()


def trigger_timer_task(game_engine):
    task_name = f"{game_engine.task_name}_clock"
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            asyncio.create_task(realtime_timer_broadcast(game_engine), name=task_name)
            return
    asyncio.create_task(realtime_timer_broadcast(game_engine), name=task_name)


async def realtime_timer_broadcast(game_engine):
    turn = game_engine.current_turn

    if turn == Color.WHITE:
        timer = game_engine.timer_white
    elif turn == Color.BLACK:
        timer = game_engine.timer_black

    while timer >= 0:
        timer -= 1
        msg = {"type": "time", "time": seconds_to_timer_format(timer), "color": turn}
        await asyncio.sleep(1)
        if timer == 0:
            winner_color = opposite_color(turn)
            if winner_color == Color.WHITE:
                game_result = GameResult.WHITEWINS_OOT
            elif winner_color == Color.BLACK:
                game_result = GameResult.BLACKWINS_OOT
            game_engine.end_game(game_result=game_result)
            msg = game_engine.get_game_end_msg()
            await channel_layer.group_send(
                game_engine.group_name, {"type": "basic_broadcast", "text": msg}
            )
            return
        else:
            await channel_layer.group_send(
                game_engine.group_name, {"type": "basic_broadcast", "text": msg}
            )


def cancel_timer_task(task_name):
    task_name = f"{task_name}_clock"
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return


def trigger_countdown_task(game_engine, user_id: int):
    task_name = f"{game_engine.task_name}_countdown_{user_id}"
    asyncio.create_task(endgame_countdown(game_engine, user_id), name=task_name)


async def endgame_countdown(game_engine, user_id):
    timer = 5
    while timer >= 0:
        timer -= 1
        await asyncio.sleep(1)
        if timer == 0:
            winner_color = opposite_color(game_engine.get_user_color(user_id))
            if winner_color == Color.WHITE:
                game_result = GameResult.WHITEWINS_ABANDONED
            elif winner_color == Color.BLACK:
                game_result = GameResult.BLACKWINS_ABANDONED
            game_engine.end_game(game_result=game_result)
            msg = game_engine.get_game_end_msg()
            await channel_layer.group_send(
                game_engine.group_name, {"type": "basic_broadcast", "text": msg}
            )
            return


def cancel_countdown_task(task_name, username):
    task_name = f"{task_name}_countdown_{username}"
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            task.cancel()
            return
