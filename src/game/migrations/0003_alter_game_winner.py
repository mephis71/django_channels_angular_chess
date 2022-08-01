# Generated by Django 3.2.9 on 2022-07-28 11:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0002_auto_20220725_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='winner', to=settings.AUTH_USER_MODEL),
        ),
    ]
