import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from game.models import GameLive, GamePuzzle
from rest_framework import exceptions

User = get_user_model()


@database_sync_to_async
def get_game_by_id(game_id):
    return GameLive.objects.select_related("player_white", "player_black").get(
        id=game_id
    )


@database_sync_to_async
def get_freeboard_game_by_user(user):
    return user.freeboard_game


async def get_user_with_jwt(token):
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"])
    except:
        raise exceptions.AuthenticationFailed(
            "Invalid authentication. Could not decode token."
        )
    try:
        user = await database_sync_to_async(User.objects.get)(pk=payload["id"])

    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed("No user matching this token was found.")
    return user


@database_sync_to_async
def get_user_with_pk(pk):
    return User.objects.get(pk=pk)


@database_sync_to_async
def get_friends_online_status(user: User):
    return list(user.friends.values("username", "is_online"))


@database_sync_to_async
def get_friends_usernames(user: User):
    return list(user.friends.values_list("username", flat=True))


@database_sync_to_async
def get_puzzle_by_id(id):
    return GamePuzzle.objects.get(id=id)
