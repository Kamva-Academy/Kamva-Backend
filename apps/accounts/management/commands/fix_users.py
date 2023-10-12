from django.core.management.base import BaseCommand
from apps.accounts.models import Participant, Member, Teamm
import os
import logging
from backup_data.problem_day_users import problem_day_users
from apps.fsm.models import FSM, PlayerWorkshop

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user of problem_day event by phone_number and nationall code from list'

    # def add_arguments(self, parser):
    #     parser.add_argument(nargs='+', type=str)

    def handle(self, *args, **options):
        fsms = FSM.objects.filter(name__contains="روز حل")
        for f in fsms:
            for i, team_info in enumerate(problem_day_users):
                print("----------")
                team = team_info['team']
                t = Teamm.objects.filter(group_name=team)[0]
                members = team_info['members']
                for user_info in members:
                    password = user_info['id']
                    member = Member.objects.get(username=password)
                    participant = Participant.objects.get(member=member)
                    self.stdout.write(
                        self.style.SUCCESS('Successfully created user %s with password %s' % (member.username, password))
                    )
                    if len(PlayerWorkshop.objects.filter(player=participant, workshop=f))==0:

                        player_workshop = PlayerWorkshop.objects.create(player=participant, workshop=f,
                                                                    current_state=f.first_state)
                if len(PlayerWorkshop.objects.filter(player=t, workshop=f))==0:
                    team_workshop = PlayerWorkshop.objects.create(player=t, workshop=f,
                                                              current_state=f.first_state)

