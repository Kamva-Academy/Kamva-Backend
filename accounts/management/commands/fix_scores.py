import logging

from django.core.management.base import BaseCommand

from fsm.models import PlayerWorkshop, Problem

logger = logging.getLogger(__file__)

class ScoreTransaction:
    class Objects:
        def filter(self, **args):
            return []
    objects = Objects()

class Command(BaseCommand):
    help = 'Get scores of a workshop'

    def handle(self, *args, **options):
        for p in Problem.objects.all():
            for player_workshop in PlayerWorkshop.objects.filter(workshop__id=22):
                max_tr = None
                for score_tr in ScoreTransaction.objects.filter(player_workshop=player_workshop,
                                                                submitted_answer__player=player_workshop.player,
                                                                submitted_answer__problem=p):
                    if max_tr is None:
                        max_tr = score_tr
                    else:
                        if max_tr.score < score_tr.score:
                            max_tr = score_tr

                    score_tr.is_valid = False
                    score_tr.save()
                if max_tr is not None:
                    max_tr.is_valid = True
                    print(f'for player_workshop {player_workshop.id} in problem {p.id} score{max_tr.score} is set true')
                    max_tr.save()
                #

            # team = Team.objects.get(player_ptr_id=player_workshop.player.id)
            # print(f'{team.group_name}: {get_scores_sum(player_workshop)}')
