# Generated by Django 4.1.3 on 2024-01-13 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0092_programcontactinfo_event_program_contact_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='programcontactinfo',
            old_name='bale_id',
            new_name='bale_link',
        ),
        migrations.RenameField(
            model_name='programcontactinfo',
            old_name='eitaa_id',
            new_name='eitaa_link',
        ),
        migrations.RenameField(
            model_name='programcontactinfo',
            old_name='instagram_id',
            new_name='instagram_link',
        ),
        migrations.RenameField(
            model_name='programcontactinfo',
            old_name='shad_id',
            new_name='shad_link',
        ),
        migrations.RenameField(
            model_name='programcontactinfo',
            old_name='telegram_id',
            new_name='telegram_link',
        ),
    ]