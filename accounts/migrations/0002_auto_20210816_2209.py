# Generated by Django 3.1 on 2021-08-16 17:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('fsm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='fsm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='fsm.fsm'),
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshops', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mentor',
            name='member',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mentor', to='accounts.member'),
        ),
        migrations.AddField(
            model_name='mentor',
            name='workshops',
            field=models.ManyToManyField(related_name='workshop_mentors', to='fsm.FSM'),
        ),
        migrations.AddField(
            model_name='eventowner',
            name='events',
            field=models.ManyToManyField(related_name='event_owners', to='fsm.Event'),
        ),
        migrations.AddField(
            model_name='eventowner',
            name='member',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='accounts.member'),
        ),
        migrations.AddField(
            model_name='educationalinstitute',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='institutes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='educationalinstitute',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='educationalinstitute',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_institutes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='educationalinstitute',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_accounts.educationalinstitute_set+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='discountcode',
            name='merchandise',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discount_codes', to='accounts.merchandise'),
        ),
        migrations.AddField(
            model_name='discountcode',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discount_codes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='schoolstudentship',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='accounts.school'),
        ),
        migrations.AddField(
            model_name='schoolstudentship',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school_studentship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='participant',
            name='event_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_participants', to='accounts.team'),
        ),
        migrations.AddField(
            model_name='participant',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_participant', to='accounts.member'),
        ),
        migrations.AddField(
            model_name='academicstudentship',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='academic_students', to='accounts.university'),
        ),
        migrations.AddField(
            model_name='academicstudentship',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic_studentship', to=settings.AUTH_USER_MODEL),
        ),
    ]