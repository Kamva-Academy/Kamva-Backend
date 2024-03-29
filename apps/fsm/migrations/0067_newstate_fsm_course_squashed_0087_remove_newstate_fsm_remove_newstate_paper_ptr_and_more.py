# Generated by Django 4.1.3 on 2024-01-05 10:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('fsm', '0066_delete_submittedanswer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0014_alter_educationalinstitute_polymorphic_ctype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer_sheet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.answersheet'),
        ),
        migrations.AlterField(
            model_name='biganswer',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.biganswerproblem'),
        ),
        migrations.AlterField(
            model_name='multichoiceanswer',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.multichoiceproblem'),
        ),
        migrations.AlterField(
            model_name='smallanswer',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.smallanswerproblem'),
        ),
        migrations.AlterField(
            model_name='uploadfileanswer',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.uploadfileproblem'),
        ),
        migrations.AddField(
            model_name='event',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.RenameField(
            model_name='certificatetemplate',
            old_name='name_X',
            new_name='name_X_percentage',
        ),
        migrations.RenameField(
            model_name='certificatetemplate',
            old_name='name_Y',
            new_name='name_Y_percentage',
        ),
        migrations.AlterField(
            model_name='certificatetemplate',
            name='name_X_percentage',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='certificatetemplate',
            name='name_Y_percentage',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fsm',
            name='order_in_program',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='choice',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='choice',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='fsm.multichoiceproblem'),
        ),
        migrations.AlterField(
            model_name='multichoiceanswer',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='fsm.multichoiceproblem'),
        ),
        migrations.RemoveField(
            model_name='multichoiceanswer',
            name='choices',
        ),
        migrations.DeleteModel(
            name='ChoiceSelection',
        ),
        migrations.AddField(
            model_name='multichoiceanswer',
            name='choices',
            field=models.ManyToManyField(to='fsm.choice'),
        ),
        migrations.RenameModel(
            old_name='Description',
            new_name='TextWidget',
        ),
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('Game', 'Game'), ('Video', 'Video'), ('Image', 'Image'), ('Aparat', 'Aparat'), ('Audio', 'Audio'), ('TextWidget', 'Textwidget'), ('SmallAnswerProblem', 'Smallanswerproblem'), ('BigAnswerProblem', 'Biganswerproblem'), ('MultiChoiceProblem', 'Multichoiceproblem'), ('UploadFileProblem', 'Uploadfileproblem'), ('Scorable', 'Scorable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('Game', 'Game'), ('Video', 'Video'), ('Image', 'Image'), ('Aparat', 'Aparat'), ('Audio', 'Audio'), ('TextWidget', 'Textwidget'), ('DetailBoxWidget', 'Detailboxwidget'), ('SmallAnswerProblem', 'Smallanswerproblem'), ('BigAnswerProblem', 'Biganswerproblem'), ('MultiChoiceProblem', 'Multichoiceproblem'), ('UploadFileProblem', 'Uploadfileproblem'), ('Scorable', 'Scorable')], max_length=30),
        ),
        migrations.CreateModel(
            name='DetailBoxWidget',
            fields=[
                ('widget_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='fsm.widget')),
                ('title', models.TextField()),
                ('details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fsm.paper')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('fsm.widget',),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paper_type',
            field=models.CharField(choices=[('RegistrationForm', 'Registrationform'), ('State', 'State'), ('Hint', 'Hint'), ('WidgetHint', 'Widgethint'), ('Article', 'Article'), ('General', 'General')], max_length=25),
        ),
        migrations.AddField(
            model_name='event',
            name='FAQs_paper_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='site_help_paper_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
