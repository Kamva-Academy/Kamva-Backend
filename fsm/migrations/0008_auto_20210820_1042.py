# Generated by Django 3.1 on 2021-08-20 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0007_registrationform_gender_partition_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_accepted', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='fsm',
            name='team_size',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='registrationreceipt',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='fsm.team'),
        ),
        migrations.AddField(
            model_name='team',
            name='team_head',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='headed_team', to='fsm.registrationreceipt'),
        ),
        migrations.DeleteModel(
            name='TeamMembership',
        ),
        migrations.AddField(
            model_name='invitation',
            name='invitee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='fsm.registrationreceipt'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='fsm.team'),
        ),
    ]