from django.core.management.base import BaseCommand
from accounts.models import Mentor, Member
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create mentor by email list'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        for mentor_email in options['email']:
            password = Member.objects.make_random_password()
            mentor = Mentor.objects.create_mentor(
                email=mentor_email,
                password=password,
                is_mentor = True,
                is_participant = False
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created mentor %s with password %s' % (mentor_email, password))
            )
            mentor.send_greeting_email(
                username=mentor_email,
                password=password
            )
