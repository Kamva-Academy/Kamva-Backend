from django.core.management.base import BaseCommand
import os
import logging

from django.utils import timezone

from fsm.models import RegistrationReceipt, Event, Player, PlayerHistory
from .users import users

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create players'

    def handle(self, *args, **options):
        for f in Event.objects.get(id=1).fsms.filter(is_active=True):
            if f.first_state:
                for r in RegistrationReceipt.objects.filter(is_participating=True):
                    if len(Player.objects.filter(user=r.user, fsm=f, receipt=r)) <= 0:
                        p = Player.objects.create(user=r.user, fsm=f, receipt=r, current_state=f.first_state, last_visit=timezone.now())
                        PlayerHistory.objects.create(player=p, state=f.first_state, start_time=p.last_visit)

                        self.stdout.write(self.style.SUCCESS(f'created_for {r.user.username} & {f.name}'))
