# Generated by Django 3.1 on 2021-08-29 13:54

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fsm', '0020_auto_20210829_1202'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('user', 'fsm')},
        ),
    ]