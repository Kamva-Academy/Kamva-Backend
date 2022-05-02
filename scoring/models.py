from operator import mod
from django.db import models
from accounts.models import *
from django.db.models import IntegerField, Model, Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from fsm.models import Answer, Paper
# Create your models here.


class ScoreType(PolymorphicModel):
    name = models.CharField(max_length=50, null=False, blank=False)
    papers = models.ManyToManyField(Paper, related_name='score_types')

    def __str__(self):
        return self.name


class Score(PolymorphicModel):
    value = IntegerField(default=0)
    score_type = models.ForeignKey(ScoreType, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='scores')
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


class BaseCondition(PolymorphicModel):

    def evaluate(self, user: User) -> bool:
        pass


class Condition(BaseCondition):
    name = models.CharField(max_length=50, null=True, blank=True)
    amount = models.IntegerField(default=0)
    score_type = models.ForeignKey(ScoreType, related_name='conditions', on_delete=models.CASCADE)

    def evaluate(self, user: User) -> bool:
        score_sum = Score.objects.filter(score_type=self.score_type, answer__submitted_by=user).aggregate(Sum('value')).get('value__sum', 0)
        return (score_sum if score_sum is not None else 0) >= self.amount

    def __str__(self):
        return f'{self.score_type.name}>={self.amount}'


class Criteria(BaseCondition):
    class Operand(models.TextChoices):
        And = "And"
        Or = "Or"

    conditions = models.ManyToManyField(BaseCondition, related_name='criterias')
    operand = models.CharField(max_length=25, blank=False, null=False, choices=Operand.choices)

    def evaluate(self, user: User) -> bool:
        result = self.operand == 'And'
        for condition in self.conditions.all():
            evaluation = condition.evaluate(user)
            result = (result and evaluation) if self.operand == 'And' else (result or evaluation)
        return result

    def __str__(self):
        return ('&' if self.operand == 'And' else '|').join(str(c) for c in self.conditions.all())