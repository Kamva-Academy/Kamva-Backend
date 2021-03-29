from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Event, Team
import os
import logging
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'set team names'

    def handle(self, *args, **options):
        for team in Team.objects.all():
            team.group_name = str(team)
            team.save()

            self.stdout.write(
                self.style.SUCCESS(f'{team.group_name}\n')
            )
