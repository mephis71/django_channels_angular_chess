from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
import os 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chess.settings')

django_asgi_app = get_asgi_application()

from game.consumers import GameChatConsumer, GameLiveConsumer, StockfishConsumer, GameFreeBoardConsumer
from users.consumers import InviteConsumer, OnlineStatusConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/invites", InviteConsumer.as_asgi()),
            path("ws/online_status", OnlineStatusConsumer.as_asgi()),
            re_path(r"^ws/game/live/(?P<game_id>[0-9]+)$", GameLiveConsumer.as_asgi()),
            re_path(r"^ws/game/live/(?P<game_id>[0-9]+)/chat", GameChatConsumer.as_asgi()),
            re_path(r"^ws/game/stockfish", StockfishConsumer.as_asgi()),
            re_path(r"^ws/game/freeboard", GameFreeBoardConsumer.as_asgi()),
        ])
    )
})
