from django.core.management.base import BaseCommand

from accounts.management.commands.tournament_users import tournament_teams
from accounts.models import Participant, Team
import logging
from fsm.models import FSM, PlayerWorkshop, Event

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user of tournament event by phone_number and national code from list'

    def add_arguments(self, parser):
        parser.add_argument('mode', nargs='+', type=str)

    def handle(self, *args, **options):
        for mode in options['mode']:
            fsm_1 = FSM.objects.get(id=1)
            fsm_2 = FSM.objects.get(id=2)
            event = Event.objects.get(id=1)
            for team in tournament_teams[mode]:
                user_1 = Participant.objects.create_participant_2(
                    phone_number=team['password_1'],
                    name=team['name_1'],
                    national_code=team['password_1'],
                )
                user_2 = Participant.objects.create_participant_2(
                    phone_number=team['password_2'],
                    name=team['name_2'],
                    national_code=team['password_2'],
                )
                user_3 = Participant.objects.create_participant_2(
                    phone_number=team['password_3'],
                    name=team['name_3'],
                    national_code=team['password_3'],
                )
                team_player = Team.objects.create(group_name=team['group_name'], team_code=team['team_code'], player_type='TEAM', active=True)
                team_player.team_members.add(user_1)
                team_player.team_members.add(user_2)
                team_player.team_members.add(user_3)
                team_player.events.add(event)
                team_player.save()
                if mode == 't1':
                    player1_f1 = PlayerWorkshop.objects.create(player=user_1, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    player2_f1 = PlayerWorkshop.objects.create(player=user_2, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    player3_f1 = PlayerWorkshop.objects.create(player=user_3, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    team_f1 = PlayerWorkshop.objects.create(player=team_player, workshop=fsm_1,
                                                            current_state=fsm_1.first_state)
                elif mode == 't2':
                    player1_f2 = PlayerWorkshop.objects.create(player=user_1, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    player2_f2 = PlayerWorkshop.objects.create(player=user_2, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    player3_f2 = PlayerWorkshop.objects.create(player=user_3, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    team_f2 = PlayerWorkshop.objects.create(player=team_player, workshop=fsm_2,
                                                            current_state=fsm_2.first_state)
                elif mode == 'test':
                    player1_f1 = PlayerWorkshop.objects.create(player=user_1, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    player2_f1 = PlayerWorkshop.objects.create(player=user_2, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    player3_f1 = PlayerWorkshop.objects.create(player=user_3, workshop=fsm_1,
                                                               current_state=fsm_1.first_state)
                    player1_f2 = PlayerWorkshop.objects.create(player=user_1, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    player2_f2 = PlayerWorkshop.objects.create(player=user_2, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    player3_f2 = PlayerWorkshop.objects.create(player=user_3, workshop=fsm_2,
                                                               current_state=fsm_2.first_state)
                    team_f1 = PlayerWorkshop.objects.create(player=team_player, workshop=fsm_1,
                                                            current_state=fsm_1.first_state)
                    team_f2 = PlayerWorkshop.objects.create(player=team_player, workshop=fsm_2,
                                                            current_state=fsm_2.first_state)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created players and player_workshops needed for team {team["group_name"]} with members {team["name_1"]}, {team["name_2"]}, {team["name_3"]}'))
