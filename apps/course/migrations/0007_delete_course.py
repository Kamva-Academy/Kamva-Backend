# Generated by Django 4.1.3 on 2024-01-01 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0087_remove_newstate_fsm_remove_newstate_paper_ptr_and_more'),
        ('course', '0006_alter_course_cover_image'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Course',
        ),
    ]
