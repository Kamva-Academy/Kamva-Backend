from django.core.management.base import BaseCommand
from apps.accounts.models import Participant, Member, Event, Teamm
import os
import logging
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'set team names'

    def handle(self, *args, **options):
        for team in Teamm.objects.all():
            team.group_name = str(team)
            team.save()

            self.stdout.write(
                self.style.SUCCESS(f'{team.group_name}\n')
            )
