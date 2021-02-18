from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Team
import os
import logging
from backup_data.problem_day_users import problem_day_users
from fsm.models import FSM, PlayerWorkshop

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user of problem_day event by phone_number and nationall code from list'

    # def add_arguments(self, parser):
    #     parser.add_argument(nargs='+', type=str)

    def handle(self, *args, **options):
        print("----------")

        # test_workshop = FSM.objects.get(name="آموزش کار در پلتفرم")
        for i, team_info in enumerate(problem_day_users):
            print("----------")
            workshop = find_workshop(i)
            team = team_info['team']
            t = Team.objects.filter(group_name=team)[0]
            members = team_info['members']
            for user_info in members:
                # user_phone = user_info['phone']
                name = user_info['name']
                password = user_info['id']
                member = Member.objects.get(username=password)
                # member.is_mentor = False
                # member.is_participant = True
                # member.save()

                participant = Participant.objects.get(member=member)
                # t.team_members.add(participant)
                self.stdout.write(
                    self.style.SUCCESS('Successfully created user %s with password %s' % (member.username, password))
                )

                player_workshop = PlayerWorkshop.objects.create(player=participant, workshop=workshop,
                                                            current_state=workshop.first_state)
                # player_workshop = PlayerWorkshop.objects.create(player=participant, workshop=test_workshop,
                #                                             current_state=workshop.first_state)
            team_workshop = PlayerWorkshop.objects.create(player=t, workshop=workshop,
                                                        current_state=workshop.first_state)
            # team_workshop2 = PlayerWorkshop.objects.create(player=t, workshop=test_workshop,
            #                                             current_state=workshop.first_state)


def find_workshop(team):
    if team < 4:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه هفتم)')
    elif 3< team<8:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه ششم)')
    elif 7< team<12:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه پنجم)')
    elif 11< team<16:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه چهارم)')
    elif  15<team<21:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه سوم)')
    elif  20< team<26:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه دوم)')
    elif 25<team<31:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه اول)')
    else:
        workshop = FSM.objects.get(name='روز حل مسئله (گروه هشتم)')
    # workshop = FSM.objects.all()[0]

    return workshop




