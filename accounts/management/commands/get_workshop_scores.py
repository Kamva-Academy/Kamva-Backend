import logging

from django.core.management.base import BaseCommand

from accounts.models import Teamm
from fsm.models import PlayerWorkshop, FSM
from fsm.views.functions import get_scores_sum

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Get scores of a workshop'

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for workshop_id in options['workshop_id']:
            print(f'----------\nfor workshop {FSM.objects.get(id=workshop_id)}\n------------')
            for player_workshop in PlayerWorkshop.objects.filter(workshop__id=workshop_id):
                team = Teamm.objects.get(player_ptr_id=player_workshop.player.id)
                print(f'{team.group_name}: {get_scores_sum(player_workshop)}')
