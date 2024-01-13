# Generated by Django 4.1.3 on 2024-01-12 23:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0091_widget_be_corrected'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramContactInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('telegram_id', models.CharField(blank=True, max_length=100, null=True)),
                ('shad_id', models.CharField(blank=True, max_length=100, null=True)),
                ('eitaa_id', models.CharField(blank=True, max_length=100, null=True)),
                ('bale_id', models.CharField(blank=True, max_length=100, null=True)),
                ('instagram_id', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='program_contact_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event', to='fsm.programcontactinfo'),
        ),
    ]