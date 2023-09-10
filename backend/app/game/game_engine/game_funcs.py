from .game_cls import Color

field_to_number_dict = {
    "a8": 0,
    "b8": 1,
    "c8": 2,
    "d8": 3,
    "e8": 4,
    "f8": 5,
    "g8": 6,
    "h8": 7,
    "a7": 8,
    "b7": 9,
    "c7": 10,
    "d7": 11,
    "e7": 12,
    "f7": 13,
    "g7": 14,
    "h7": 15,
    "a6": 16,
    "b6": 17,
    "c6": 18,
    "d6": 19,
    "e6": 20,
    "f6": 21,
    "g6": 22,
    "h6": 23,
    "a5": 24,
    "b5": 25,
    "c5": 26,
    "d5": 27,
    "e5": 28,
    "f5": 29,
    "g5": 30,
    "h5": 31,
    "a4": 32,
    "b4": 33,
    "c4": 34,
    "d4": 35,
    "e4": 36,
    "f4": 37,
    "g4": 38,
    "h4": 39,
    "a3": 40,
    "b3": 41,
    "c3": 42,
    "d3": 43,
    "e3": 44,
    "f3": 45,
    "g3": 46,
    "h3": 47,
    "a2": 48,
    "b2": 49,
    "c2": 50,
    "d2": 51,
    "e2": 52,
    "f2": 53,
    "g2": 54,
    "h2": 55,
    "a1": 56,
    "b1": 57,
    "c1": 58,
    "d1": 59,
    "e1": 60,
    "f1": 61,
    "g1": 62,
    "h1": 63,
}

number_to_field_dict = {
    0: "a8",
    1: "b8",
    2: "c8",
    3: "d8",
    4: "e8",
    5: "f8",
    6: "g8",
    7: "h8",
    8: "a7",
    9: "b7",
    10: "c7",
    11: "d7",
    12: "e7",
    13: "f7",
    14: "g7",
    15: "h7",
    16: "a6",
    17: "b6",
    18: "c6",
    19: "d6",
    20: "e6",
    21: "f6",
    22: "g6",
    23: "h6",
    24: "a5",
    25: "b5",
    26: "c5",
    27: "d5",
    28: "e5",
    29: "f5",
    30: "g5",
    31: "h5",
    32: "a4",
    33: "b4",
    34: "c4",
    35: "d4",
    36: "e4",
    37: "f4",
    38: "g4",
    39: "h4",
    40: "a3",
    41: "b3",
    42: "c3",
    43: "d3",
    44: "e3",
    45: "f3",
    46: "g3",
    47: "h3",
    48: "a2",
    49: "b2",
    50: "c2",
    51: "d2",
    52: "e2",
    53: "f2",
    54: "g2",
    55: "h2",
    56: "a1",
    57: "b1",
    58: "c1",
    59: "d1",
    60: "e1",
    61: "f1",
    62: "g1",
    63: "h1",
}

piece_str_to_fen_letter_dict = {
    "whitepawn": "P",
    "whiteknight": "N",
    "whitebishop": "B",
    "whiterook": "R",
    "whiteking": "K",
    "whitequeen": "Q",
    "blackpawn": "p",
    "blackknight": "n",
    "blackbishop": "b",
    "blackrook": "r",
    "blackking": "k",
    "blackqueen": "q",
}


def field_to_number(field: str) -> int:
    return field_to_number_dict[field]


def number_to_field(number: int) -> str:
    return number_to_field_dict[number]


def piece_str_to_fen_letter(piece_str: str) -> str:
    return piece_str_to_fen_letter_dict[piece_str]


def seconds_to_timer_format(seconds):
    s = seconds
    m = s // 60
    s = s - m * 60
    if m < 10:
        m = f"0{m}"
    if s < 10:
        s = f"0{s}"
    return f"{m}:{s}"


def timer_format_to_seconds(timer):
    timer = timer.split(":")
    minutes = int(timer[0])
    seconds = int(timer[1])
    return (minutes * 60) + seconds


def to_timestamp(timers):
    """Takes an array of timers in seconds and outputs it in timer_format -> ('05:00', '03:19')"""
    return tuple([seconds_to_timer_format(timer) for timer in timers])


def to_seconds(timers):
    """Takes an array of timers in timer format and outputs it in seconds -> (300, 199)"""
    return tuple([timer_format_to_seconds(timer) for timer in timers])


def opposite_color(color):
    if color == Color.BLACK:
        return Color.WHITE
    elif color == Color.WHITE:
        return Color.BLACK
