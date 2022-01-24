from django.core.management.base import BaseCommand
from accounts.models import Participant, Member, Teamm
import os
import logging
from backup_data.problem_day_users import problem_day_users
from fsm.models import FSM, PlayerWorkshop, SubmittedAnswer

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create mentor by email list'

    def handle(self, *args, **options):
        d_list = {-1}
        fsm = FSM.objects.get(name='سیستم‌های پیشنهاددهنده')
        for submit in SubmittedAnswer.objects.filter(problem__state__mainstate__fsm=fsm):
            last_submit = SubmittedAnswer.objects.filter(problem__state__mainstate__fsm=fsm,
                                                         player=submit.player, problem=submit.problem).order_by('-id')[
                0]
            print(last_submit.id)
            d_list.add(last_submit.id)
        for submit in SubmittedAnswer.objects.filter(problem__state__mainstate__fsm=fsm):
            if submit.id not in d_list:
                submit.delete()
                print("submit deleted")
