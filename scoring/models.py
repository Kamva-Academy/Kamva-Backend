from django.db import models
from fsm.models import PlayerWorkshop, SubmittedAnswer
from .managers import ScoringManager


class ScoreTransaction(models.Model):
    score = models.FloatField(default=0, blank=True)
    description = models.TextField(null=True, blank=True)
    player_workshop = models.ForeignKey(PlayerWorkshop, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True, null=False)
    submitted_answer = models.OneToOneField(SubmittedAnswer, related_name='review', on_delete=models.CASCADE, null=True, blank=True)

    objects = ScoringManager()

    def __str__(self):
        return f'{str(self.player_workshop)}:{self.score}'
