from django.core.management.base import BaseCommand
import os
import logging

from django.utils import timezone

from fsm.models import RegistrationReceipt, Event, Player
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create players'

    def handle(self, *args, **options):
        for f in Event.objects.get(id=1).fsms.all():
            for r in RegistrationReceipt.objects.filter(is_participating=True):
                if len(Player.objects.filter(user=r.user, fsm=f, receipt=r)) <= 0:
                    Player.objects.create(user=r.user, fsm=f, receipt=r, current_state=f.first_state, last_visit=timezone.now())

        #
        #
        # data = {'user': r.user.id, 'fsm': fsm.id, 'receipt': r.id,
        #         'current_state': fsm.first_state.id, 'last_visit': timezone.now()}


                    self.stdout.write(self.style.SUCCESS(f'created_for {r.user.username} & {f.name}'))

