# Generated by Django 3.0.8 on 2021-03-29 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0009_auto_20210327_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='fsmedge',
            name='has_lock',
            field=models.BooleanField(default=False),
        ),
    ]