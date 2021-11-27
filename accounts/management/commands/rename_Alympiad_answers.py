import os

from django.conf import settings
from django.core.management import BaseCommand

from fsm.models import RegistrationForm, Problem, UploadFileProblem


class Command(BaseCommand):
    help = 'Create users and teams'

    def add_arguments(self, parser):
        parser.add_argument('registration_form', nargs='+', type=str)
        parser.add_argument('problem', nargs='+', type=str)

    def handle(self, *args, **options):
        form_id = options['registration_form'][0]
        problem_id = options['problem'][0]
        registration_form = RegistrationForm.objects.get(id=form_id)
        upload_problem = UploadFileProblem.objects.get(id=problem_id)
        for t in registration_form.teams.all():
            team_head_id = t.team_head.id
            for m in t.members.all():
                for a in upload_problem.answers.filter(is_final_answer=True, submitted_by=m.user):
                    answer_file = a.answer_file
                    suffix = answer_file.name[answer_file.name.rfind('.'):]
                    old = answer_file.path
                    answer_file.name = f'/answers/{problem_id}-{team_head_id}{suffix}'
                    new = settings.MEDIA_ROOT + answer_file.name
                    os.rename(old, new)
                    a.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully rename to {answer_file.name}'))
