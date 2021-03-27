from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Participant, Member, PlayerWorkshop, PlayerHistory
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
                state=pw.fsm.first_state,
                start_time=timezone.now(),
                inward_edge=None
            )
            pw.current_state = pw.fsm.first_state

