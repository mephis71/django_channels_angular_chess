# Generated by Django 3.2.9 on 2022-08-19 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20220816_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='turn',
        ),
    ]