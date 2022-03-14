from operator import mod
from django.db import models
from accounts.models import *
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator
from fsm.models import Answer, Paper
# Create your models here.


class ScoreType(PolymorphicModel):
    name = models.CharField(max_length=50, null=False, blank=False)
    papers = models.ManyToManyField(Paper, related_name='scoreTypes')

    def __str__(self):
        return self.name


class Score(PolymorphicModel):
    value = IntegerField(default=0)
    score_type = models.ForeignKey(ScoreType, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    # todo: make score unique per answer-scoreType

    def __str__(self):
        return f'{self.value} × {self.score_type}'


class Comment(models.Model):
    content = models.TextField(null=False, blank=False)
    writer = models.ForeignKey('accounts.User', related_name='comments', null=True, blank=True,
                               on_delete=models.SET_NULL)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:30]
