import logging
import csv

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand

from apps.accounts.models import User

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user by phone_number list'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        with open(filename, 'r') as file:
            for data in csv.DictReader(file):
                if 'phone_number' not in list(data.keys()) or 'password' not in list(data.keys()):
                    continue
                if 'username' not in data.keys():
                    data['username'] = data['phone_number']
                data['password'] = make_password(data['password'])
                user = User.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.username} with pass {user.password}'))
