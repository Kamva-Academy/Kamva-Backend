# Generated by Django 4.2.9 on 2024-02-22 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoring', '0014_scoretype_icon_alter_scoretype_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
