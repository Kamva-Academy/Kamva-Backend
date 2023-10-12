from django.core.management.base import BaseCommand
from apps.accounts.models import Participant, Member, Teamm
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create users'

    def handle(self, *args, **options):
        for i in range(2, 20):
            username = f'user_{i}'
            password = '123456'

            current_event = Event.objects.get(name='مسافر صفر')

            team_code = Member.objects.make_random_password(length=6)

            member = Member.objects.create(
                username=username,
                is_active=True,
            )
            member.set_password(password)

            participant = Participant.objects.create(
                member=member,
                event=current_event,
                player_type='PARTICIPANT',
                is_paid=True,
                is_accepted=True,
                is_participated=True,
            )

            team = Teamm.objects.create(team_code=team_code, event=current_event, player_type='TEAM', )
            participant.event_team = team

            member.save()
            participant.save()

            self.stdout.write(
                self.style.SUCCESS('Successfully created user %s with password %s' % (username, password))
            )
