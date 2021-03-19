from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Team
import os
import logging
from backup_data.problem_day_users import problem_day_users
from fsm.models import FSM, PlayerWorkshop

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user by phone_number list'

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', nargs='+', type=str)

    def handle(self, *args, **options):
        print("----------")
        for workshop_id in options['workshop_id']:
            workshop = FSM.objects.get(id=int(workshop_id))
            # test_workshop = FSM.objects.get(name="آموزش کار در پلتفرم")
            teams = Team.objects.filter(event__name="مسافر صفر")
            for t in teams:
                if len(PlayerWorkshop.objects.filter(player=t)) <= 0:
                    PlayerWorkshop.objects.create(player=t, workshop=workshop, current_state=workshop.first_state)
                # player_workshop = PlayerWorkshop.objects.create(player=participant, workshop=test_workshop,
                #                                             current_state=workshop.first_state)
            # team_workshop = PlayerWorkshop.objects.create(player=t, workshop=workshop,
            #                                             current_state=workshop.first_state)
            # team_workshop2 = PlayerWorkshop.objects.create(player=t, workshop=test_workshop,
            #                                             current_state=workshop.first_state)

