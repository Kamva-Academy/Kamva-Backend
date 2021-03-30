from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Team
import os
import logging

from fsm.models import PlayerWorkshop, FSM, FSMEdge
from fsm.views.functions import get_scores_sum
from scoring.models import ScoreTransaction
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Get scores of a workshop'

    def handle(self, *args, **options):
        for player_workshop in PlayerWorkshop.objects.filter(workshop__id=22):
            for score_tr in ScoreTransaction.objects.filter(player_workshop=player_workshop,):
                if 0 < score_tr.score:
                    score_tr.is_valid = True
                    score_tr.save()


            # team = Team.objects.get(player_ptr_id=player_workshop.player.id)
            # print(f'{team.group_name}: {get_scores_sum(player_workshop)}')
