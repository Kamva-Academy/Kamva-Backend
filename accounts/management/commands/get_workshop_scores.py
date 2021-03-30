from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Team
import os
import logging

from fsm.models import PlayerWorkshop
from fsm.views.functions import get_scores_sum
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Get scores of a workshop'

    def add_arguments(self, parser):
        parser.add_argument('workshop', nargs='+', type=str)

    def handle(self, *args, **options):
        for player_workshop in PlayerWorkshop.objects.filter(workshop=options['workshop']):
            team = Team.objects.get(player_ptr_id=player_workshop.player.id)
            print(f'{team.group_name}: {get_scores_sum(player_workshop)}')
