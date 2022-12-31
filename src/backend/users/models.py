from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    friends = models.ManyToManyField('User')

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    def get_friend_requests(self):
        f_requests = FriendRequest.objects.filter(to_user=self.pk)
        output = []
        for req in f_requests:
            item = {
                "username": req.from_user.username,
                "id": req.id
            }
            output.append(item)
        return output

    def get_friends_list(self):
        output = []
        for friend in self.friends.all():
            output.append(friend.username)
        return output

class UserProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/', default='profile_pics/blank_profile_pic.png')
    game_history = models.ManyToManyField('game.Game')
    username = models.CharField(max_length=50, unique=True)
    
    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.username = self.user.username

    def __str__(self):
        return self.user.username

    def get_profile_pic(self):
        if not self.profile_pic:
            return '/img/profile_pics/blank_profile_pic.png'
        else:
            return self.profile_pic.url

    def get_game_history(self):
        return self.game_history.all().order_by('-game_end_time')

        
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')

    def accept(self):
        self.from_user.friends.add(self.to_user)
        self.to_user.friends.add(self.from_user)
        self.delete()