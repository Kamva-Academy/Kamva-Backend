# Generated by Django 3.0.8 on 2020-11-11 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20201110_1337'),
        ('fsm', '0003_auto_20201110_1100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedanswer',
            name='participant',
        ),
        migrations.AddField(
            model_name='submittedanswer',
            name='player',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='submited_answers', to='accounts.Player'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('Game', 'Game'), ('Video', 'Video'), ('Image', 'Image'), ('Description', 'Description'), ('ProblemSmallAnswer', 'Problemsmallanswer'), ('ProblemBigAnswer', 'Problembiganswer'), ('ProblemMultiChoice', 'Problemmultichoice'), ('ProblemUploadFileAnswer', 'Problemuploadfileanswer')], max_length=30),
        ),
    ]
