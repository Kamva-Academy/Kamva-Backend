# Generated by Django 4.1.3 on 2024-02-09 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.TextField()),
                ('text', models.TextField()),
                ('email', models.CharField(max_length=36)),
            ],
        ),
    ]
