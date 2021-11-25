from django.db import models
from django.db.models.fields import CharField
from django.contrib.auth.models import User


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='temp')
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/', default='profile_pics/blank_profile_pic.png')

    def get_profile_pic(self):
        if not self.profile_pic:
            return '/img/profile_pics/blank_profile_pic.png'
        else:
            return self.profile_pic.url

    


    