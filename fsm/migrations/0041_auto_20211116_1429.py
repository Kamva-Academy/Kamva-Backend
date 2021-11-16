# Generated by Django 3.1 on 2021-11-16 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0040_auto_20211116_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='duration',
            field=models.DurationField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='paper',
            name='is_exam',
            field=models.BooleanField(default=False),
        ),
    ]
