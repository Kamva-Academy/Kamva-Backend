import logging

from django.core.management import BaseCommand

from scoring.models import Score

logger = logging.getLogger(__file__)

PAPER_WEIGHT = {
    509: 3,
    479: 3,
    489: 3,
    490: 3,
    491: 3,
    492: 1,
}


class Command(BaseCommand):
    help = 'Multiple score values according to problem weight'

    def handle(self, *args, **options):
        scores = Score.objects.all()
        for score in scores:
            paper_id = score.answer.problem.paper.id
            if paper_id in PAPER_WEIGHT.keys():
                score.value = score.value * PAPER_WEIGHT[paper_id]
                score.save()
