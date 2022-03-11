from operator import mod
from tkinter import CASCADE
from django.db import models
from django.forms import CharField
from accounts.models import *
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator
from fsm.models import BigAnswer, UploadFileAnswer, Paper
# Create your models here.

class ScoreType(PolymorphicModel):
    score_type = CharField()
    papers = models.ManyToManyField(Paper, related_name='scoreTypes')

class Score(PolymorphicModel):
    score_value = IntegerField(default=0)
    score_type = models.ForeignKey(ScoreType, on_delete=models.CASCADE)
    answer = models.ForeignKey(BigAnswer, on_delete=models.CASCADE)

class Comment(models.Model):
    content = CharField(max_length=250, null = False, blank=False)
    writer = models.ForeignKey('accounts.User', related_name='comments', null=True, blank=True,
                                on_delete=models.SET_NULL)