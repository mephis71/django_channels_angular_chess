from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from game.api.serializers import RetrieveGameSerializer
from game.models import Game
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import FriendRequest, User, UserProfile

from .serializers import (
    FriendRequestSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
    UserSerializer,
)

channel_layer = get_channel_layer()


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        register_info = request.data.get("register_info", {})
        serializer = self.serializer_class(data=register_info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        login_info = request.data.get("login_info", {})
        serializer = self.serializer_class(data=login_info)
        serializer.is_valid(raise_exception=True)
        response = Response(
            data=UserSerializer(serializer.validated_data["user"]).data,
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="jwt",
            value=serializer.validated_data["token"],
            httponly=True,
            samesite=None,
        )
        return response


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie("jwt")
        return response


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get("user", {})
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SendFriendRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def post(self, request, *args, **kwargs):
        to_username = request.data.get("to_username")
        to_user = User.objects.filter(username=to_username).first()
        if to_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            data = {"from_user": request.user.id, "to_user": to_user.id}
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                self.send_ws_msg(serializer.instance)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_ws_msg(self, data):
        to_user_id = data.to_user.id
        from_user_id = data.from_user.id
        from_user_username = data.from_user.username
        invite_id = data.id
        
        data = {
            'type': 'friend_request',
            'from_user_id': from_user_id,
            'from_user_username': from_user_username,
            'invite_id': invite_id
        }

        async_to_sync(channel_layer.group_send)(
            f"{to_user_id}_system",
            {
                "type": "system_message",
                "text": data
            }
        )


class AcceptFriendRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        friend_request_id = kwargs["id"]
        friend_request = FriendRequest.objects.filter(id=friend_request_id).first()
        if friend_request is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            friend = friend_request.from_user
            friend_request.accept()
            self.send_ws_msg(friend.username, friend_request.to_user)
            data = {"friend_username": friend.username, "is_online": friend.is_online}
            return Response(data, status=status.HTTP_200_OK)

    def send_ws_msg(self, msg_target_id, user):
        async_to_sync(channel_layer.group_send)(
            f"{msg_target_id}_system",
            {
                "type": "system_message",
                "text": {
                    "type": "add_friend",
                    "friend_id": user.id,
                    "is_online": user.is_online,
                },
            },
        )


class RejectFriendRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        friend_request_id = kwargs["id"]
        friend_request = FriendRequest.objects.filter(id=friend_request_id).first()
        if friend_request is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            friend_request.reject()
            return Response(status=status.HTTP_200_OK)


class RemoveFriendAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        friend_username = kwargs["friend_username"]
        friend = User.objects.filter(username=friend_username).first()
        if friend is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
            user.friends.remove(friend)
            friend.friends.remove(user)
            self.send_ws_msg(friend.username, user.username)
            return Response(status=status.HTTP_200_OK)

    def send_ws_msg(self, msg_target_id, username):
        async_to_sync(channel_layer.group_send)(
            f"{msg_target_id}_system",
            {
                "type": "system_message",
                "text": {"type": "remove_friend", "friend_username": username},
            },
        )


class UserProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        username = kwargs["username"]
        profile = UserProfile.objects.filter(username=username).first()
        if profile is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.serializer_class(instance=profile)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserRunningGamesAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveGameSerializer

    def get(self, request, *args, **kwargs):
        username = request.user.username
        qs = Game.objects.get_running_games(username)
        if qs is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.serializer_class(instance=qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
