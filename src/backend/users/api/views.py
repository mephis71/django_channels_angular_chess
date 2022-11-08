from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer, FriendRequestSerializer
from users.models import User, FriendRequest

class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='jwt', value=serializer.validated_data['token'], httponly=True, samesite=None)
        return response

class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('jwt')
        return response

class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
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
        to_username = request.data.get('to_username')
        to_user = User.objects.filter(username=to_username).first()
        if to_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            data = {
                "from_user": request.user.id,
                "to_user": to_user.id
            }
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()   
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptFriendRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        friend_request_id = kwargs['id']
        friend_request = FriendRequest.objects.filter(id=friend_request_id).first()
        if friend_request is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            friend_request.accept()
            return Response(status=status.HTTP_202_ACCEPTED)

        