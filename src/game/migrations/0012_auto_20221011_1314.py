# Generated by Django 3.2.9 on 2022-10-11 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_game_last_move_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='timer_black',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='game',
            name='timer_white',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
