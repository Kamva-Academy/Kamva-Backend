from django.db import models
from fsm.models import PlayerWorkshop
from .managers import ScoringManager


class ScoreTransaction(models.Model):
    score = models.FloatField(default=0, blank=True)
    description = models.TextField(null=True, blank=True)
    player_workshop = models.ForeignKey(PlayerWorkshop, on_delete=models.CASCADE)

    objects = ScoringManager()
