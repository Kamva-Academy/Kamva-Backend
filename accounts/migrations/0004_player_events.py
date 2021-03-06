# Generated by Django 3.0.8 on 2021-03-06 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0006_article'),
        ('accounts', '0003_verifycode'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='events',
            field=models.ManyToManyField(related_name='event_players', to='fsm.Event'),
        ),
    ]
