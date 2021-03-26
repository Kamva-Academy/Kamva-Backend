from django.db import models
from fsm.models import PlayerWorkshop
from .managers import ScoringManager
from fsm.models import Answer


class ScoreTransaction(models.Model):
    score = models.FloatField(default=0, blank=True)
    description = models.TextField(null=True, blank=True)
    player_workshop = models.ForeignKey(PlayerWorkshop, on_delete=models.CASCADE)

    objects = ScoringManager()
    source = models.ForeignKey(Answer, related_name='reviews', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{str(self.player_workshop)}:{self.score}'
