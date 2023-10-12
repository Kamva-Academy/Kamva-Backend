from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Participant, Member, PlayerWorkshop, PlayerHistory
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create user by phone_number list'

    # def add_arguments(self, parser):
    #     parser.add_argument(nargs='+', type=str)

    def handle(self, *args, **options):
        for pw in PlayerWorkshop.objects.all():
            history = PlayerHistory.objects.create(
                player_workshop=pw,
                state=pw.workshop.first_state,
                start_time=timezone.now(),
                inward_edge=None
            )
            print(f'added history for {str(pw)}')
            pw.current_state = pw.workshop.first_state

