# Generated by Django 3.1 on 2021-12-09 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0043_auto_20211127_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationform',
            name='audience_check_status',
            field=models.CharField(choices=[('Student', 'Student'), ('Academic', 'Academic'), ('All', 'All')], default='Student', max_length=50),
        ),
    ]
