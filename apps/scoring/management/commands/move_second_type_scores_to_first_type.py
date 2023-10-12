import logging

from django.core.management import BaseCommand
from django.db import transaction

from apps.scoring.models import Score

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Move second type score to first type'

    @transaction.atomic
    def handle(self, *args, **options):
        second_type_scores = Score.objects.filter(type__id=2)
        for second_type_score in second_type_scores:
            first_type_score = Score.objects.filter(type__id=1, answer=second_type_score.answer)
            if len(first_type_score) > 0:
                first_type_score = first_type_score.first()
                first_type_score.value = second_type_score.value
                first_type_score.save()

    print("Done!")
