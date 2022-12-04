def to_timer_format(seconds):
        s = int(seconds)
        m = s//60
        s = s - m*60
        if m < 10:
            m = f'0{m}'
        if s < 10:
            s = f'0{s}'
        return f'{m}:{s}'

def opposite_color(color):
    if color == 'black':
        return 'white'
    else:
        return 'black'

def init_JSON(game_obj, username):
    fen = game_obj.fen
    current_turn = game_obj.get_turn()
    player_color = game_obj.get_color(username)
    time_black = to_timer_format(game_obj.timer_black)
    time_white = to_timer_format(game_obj.timer_white)
    game_positions = game_obj.get_game_positions()
    data = {
        'type': 'init',
        'fen': fen,
        'player_color': player_color,
        'current_turn': current_turn,
        'time_black': time_black,
        'time_white': time_white,
        'game_positions': game_positions
    }
    return data

def move_JSON(game_obj):
    fen = game_obj.fen
    current_turn = game_obj.get_turn()
    time_black = to_timer_format(game_obj.timer_black)
    time_white = to_timer_format(game_obj.timer_white)
    game_positions = game_obj.get_game_positions()
    data = {
        'type': 'move',
        'fen': fen,
        'current_turn': current_turn,
        'time_black': time_black,
        'time_white': time_white,
        'game_positions': game_positions
    }
    return data

def endgame_JSON(game_obj, game_result):
    fen = game_obj.fen
    current_turn = game_obj.get_turn()
    time_black = to_timer_format(game_obj.timer_black)
    time_white = to_timer_format(game_obj.timer_white)
    game_positions = game_obj.get_game_positions()
    data = {
        'type': 'endgame',
        'fen': fen,
        'current_turn': current_turn,
        'time_black': time_black,
        'time_white': time_white,
        'game_result': game_result,
        'game_positions': game_positions
    }
    return data


