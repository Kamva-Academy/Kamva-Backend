# Generated by Django 3.1 on 2022-08-17 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0056_team_chat_room'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=set(),
        ),
    ]
