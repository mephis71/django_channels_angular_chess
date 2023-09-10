import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from game.consumers import (
    GameChatConsumer,
    GameFreeBoardConsumer,
    GameLiveConsumer,
    GamePuzzleConsumer,
    StockfishConsumer,
)
from users.consumers import InviteConsumer, OnlineStatusConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_chess.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/invites", InviteConsumer.as_asgi()),
                    path("ws/online_status", OnlineStatusConsumer.as_asgi()),
                    re_path(
                        r"^ws/game_in_progress/(?P<game_id>[0-9]+)$",
                        GameLiveConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/game/live/(?P<game_id>[0-9]+)/chat",
                        GameChatConsumer.as_asgi(),
                    ),
                    path("ws/game/stockfish", StockfishConsumer.as_asgi()),
                    path("ws/game/freeboard", GameFreeBoardConsumer.as_asgi()),
                    re_path(
                        r"^ws/game/puzzle/(?P<puzzle_id>[0-9]+)$",
                        GamePuzzleConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
