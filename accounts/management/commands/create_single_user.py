from django.core.management.base import BaseCommand
from accounts.models import Participant, Member
import os
import logging
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user by phone_number list'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['username']:
            user, password = Participant.objects.create_participant(
                username=username,
                name=username,
                is_user=True,
                is_participant=True,
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created user %s with password %s' % (username, password))
            )

