from django.contrib.auth import get_user_model

User = get_user_model()

users = User.objects.all()
users.update(is_online=False)
