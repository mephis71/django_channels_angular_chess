# Generated by Django 3.2.9 on 2022-09-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_game_moves_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='moves_list',
            field=models.TextField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'),
        ),
    ]