from rest_framework import serializers
from users.models import User, FriendRequest
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        email = data.get('email', None)

        if username is None:
            raise serializers.ValidationError({"username": 'An username is required to register.'})
        if password is None:
            raise serializers.ValidationError({"password": 'A password is required to register.'})
        if email is None or email == '':
            raise serializers.ValidationError({"email": 'An email is required to register.'})

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None:
            raise serializers.ValidationError({"username": 'An username is required to log in.'})
        if password is None:
            raise serializers.ValidationError({"password": 'A password is required to log in.'})

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('A user with this username and password was not found.')
        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')

        return {
            'token': user.token
        }


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ('from_user', 'to_user')
    
    def validate(self, data):
        to_user = data.get('to_user')
        from_user = data.get('from_user')
 
        if to_user.friends.filter(pk=from_user.id) and from_user.friends.filter(pk=to_user.id):
            raise serializers.ValidationError({"friend_request": 'You are already friends with this user'})
        if to_user == from_user:
            raise serializers.ValidationError({"friend_request": 'You can not invite yourself'})
        existing_request = FriendRequest.objects.filter(to_user=to_user, from_user=from_user).first()
        if existing_request:
            raise serializers.ValidationError({"friend_request": 'You have already sent a friend request to this user'})
        else:
            existing_request = FriendRequest.objects.filter(to_user=from_user, from_user=to_user).first()
            if existing_request:
                raise serializers.ValidationError({"friend_request": 'This user already sent a friend request to you'})
        return data
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    friend_requests = serializers.ListField(source='get_friend_requests')
    friends = serializers.ListField(source='get_friends_list')

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'friend_requests', 'friends')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance