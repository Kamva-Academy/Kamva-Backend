from django.core.management.base import BaseCommand

from accounts.management.commands.users import t_hashtom, t_dahom
from accounts.models import Participant, Member, Team
import os
import logging
from backup_data.problem_day_users import problem_day_users
from fsm.models import FSM, PlayerWorkshop, PlayerHistory

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user of problem_day event by phone_number and nationall code from list'

    def add_arguments(self, parser):
        parser.add_argument('grade', nargs='+', type=str)

    def handle(self, *args, **options):
        grade = int(options['grade'][0])
        if grade == 8:
            fsm = FSM.objects.get(name__contains="هشتم")
            users = t_hashtom
        else:
            fsm = FSM.objects.get(name__contains="دهم")
            users = t_dahom

        for i, team_info in enumerate(users):
            print("----------")
            team = team_info['team']
            t = Team.objects.filter(group_name=team)[0]
            members = team_info['members']
            for user_info in members:
                password = user_info['id']
                member = Member.objects.get(username=password)
                participant = Participant.objects.get(member=member)

                for state in fsm.states.all():
                    if len(PlayerHistory.objects.filter(player=participant, state=state))==0:
                        player_history = PlayerHistory.objects.create(player=participant, state=state)
                        print(state.name + "done"+ participant.member.username)
                    else:
                        print("no history")

            workshop_player = PlayerWorkshop.objects.filter(player=t, workshop=fsm)
            team_workshop_player = PlayerWorkshop.objects.filter(player=participant, workshop=fsm)
            if len(PlayerWorkshop.objects.filter(player=t, workshop=fsm))==0:
                team_workshop = PlayerWorkshop.objects.create(player=t, workshop=fsm,
                                                          current_state=fsm.first_state)
                print(participant.member.username)
            else:
                team_workshop_player = team_workshop_player[0]
                team_workshop_player.current_state = fsm.first_state
                team_workshop_player.save()
                workshop_player = workshop_player[0]
                workshop_player.current_state = fsm.first_state
                workshop_player.save()
                
            

