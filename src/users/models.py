from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/', default='profile_pics/blank_profile_pic.png')
    friends = models.ManyToManyField('CustomUser', blank=True)

    def __str__(self):
        return self.username
        
    def get_profile_pic(self):
        if not self.profile_pic:
            return '/img/profile_pics/blank_profile_pic.png'
        else:
            return self.profile_pic.url


class FriendRequest(models.Model):
    from_user_id = models.IntegerField(name='from_user_id')
    from_user_username = models.TextField(name='from_user_username')
    to_user_id = models.IntegerField(name='to_user_id')
    to_user_username = models.TextField(name='to_user_username')
