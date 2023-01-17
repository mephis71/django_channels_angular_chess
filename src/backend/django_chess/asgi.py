from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from game.consumers import GameChatConsumer, GameConsumer, InviteConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("game/invite/", InviteConsumer.as_asgi()),
            re_path(r"^game/live/(?P<game_id>[0-9]+)$", GameConsumer.as_asgi()),
            re_path(r"^game/live/(?P<game_id>[0-9]+)/chat", GameChatConsumer.as_asgi()),
        ])
    )
})