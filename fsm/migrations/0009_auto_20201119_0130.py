# Generated by Django 3.0.8 on 2020-11-18 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0008_auto_20201117_0206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='priority',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]