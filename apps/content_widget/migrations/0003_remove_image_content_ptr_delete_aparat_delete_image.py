# Generated by Django 4.1.3 on 2024-01-02 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_widget', '0002_rename_description_textwidget'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='content_ptr',
        ),
        migrations.DeleteModel(
            name='Aparat',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
