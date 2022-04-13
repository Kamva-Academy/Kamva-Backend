# Generated by Django 3.1 on 2022-04-13 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0051_remove_event_crispwebsiteid'),
        ('scoring', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoretype',
            name='papers',
            field=models.ManyToManyField(related_name='score_types', to='fsm.Paper'),
        ),
    ]
