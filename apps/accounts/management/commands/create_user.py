from django.core.management.base import BaseCommand
from apps.accounts.models import Participant, Member
import os
import logging
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user by phone_number list'

    # def add_arguments(self, parser):
    #     parser.add_argument(nargs='+', type=str)

    def handle(self, *args, **options):
        user_info = users
        for user_info in users:
            user_phone = user_info['phone']
            name = user_info['name']
            user, password = Participant.objects.create_participant_send_sms(
                phone_number=user_phone,
                username=user_phone,
                name=name,
                is_user=True,
                is_participant=True
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created user %s with password %s' % (user_phone, password))
            )

