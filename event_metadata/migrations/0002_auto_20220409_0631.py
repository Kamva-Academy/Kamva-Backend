# Generated by Django 3.1 on 2022-04-09 02:01

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fsm', '0051_remove_event_crispwebsiteid'),
        ('event_metadata', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staffinfo',
            old_name='account',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='staffinfo',
            unique_together={('user', 'registration_form')},
        ),
    ]