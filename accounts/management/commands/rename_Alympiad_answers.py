import os

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.management import BaseCommand

from fsm.models import RegistrationForm, Problem, UploadFileProblem, Team


class Command(BaseCommand):
    help = 'Create users and teams'

    def add_arguments(self, parser):
        parser.add_argument('problem', nargs='+', type=str)

    def handle(self, *args, **options):
        problem_id = options['problem'][0]
        upload_problem = UploadFileProblem.objects.get(id=problem_id)
        i = 0
        for a in upload_problem.answers.filter(is_final_answer=True):
            try:
                team = Team.objects.get_team_from_widget(a.submitted_by, upload_problem)
                answer_file = a.answer_file
                suffix = answer_file.name[answer_file.name.rfind('.'):]
                old = answer_file.path
                answer_file.name = f'/answers/{problem_id}-{team.team_head.id}{suffix}'
                new = settings.MEDIA_ROOT + answer_file.name
                os.rename(old, new)
                a.save()
            except SuspiciousFileOperation:
                i += 1
                print('oh')
                if i > 10:
                    break
                continue
            self.stdout.write(self.style.SUCCESS(f'Successfully rename to {answer_file.name}'))
