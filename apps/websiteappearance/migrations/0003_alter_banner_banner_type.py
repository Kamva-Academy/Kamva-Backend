# Generated by Django 4.1.3 on 2024-01-12 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websiteappearance', '0002_rename_image_banner_desktop_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='banner_type',
            field=models.CharField(choices=[('ProgramsPage', 'Programs Page'), ('ProgramPage', 'Program Page')], default='ProgramsPage', max_length=30),
        ),
    ]
