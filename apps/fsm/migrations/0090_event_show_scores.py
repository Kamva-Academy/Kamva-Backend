# Generated by Django 4.1.3 on 2024-01-05 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0089_widget_cost_widget_reward'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='show_scores',
            field=models.BooleanField(default=False),
        ),
    ]