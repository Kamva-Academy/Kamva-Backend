from django.db import models
from fsm.models import PlayerWorkshop, SubmittedAnswer, Player, Answer
from .managers import ScoringManager


class ScoreType(models.Model):
    name = models.CharField(max_length=30)


class ScoreTransaction(models.Model):
    score = models.FloatField(default=0, blank=True)
    type = models.ForeignKey(ScoreType, related_name='transactions', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True, null=False)
    answer = models.OneToOneField(Answer, related_name='review', on_delete=models.CASCADE, null=True, blank=True)

    objects = ScoringManager()

    def __str__(self):
        return f'{str(self.player)}:{self.score}'
