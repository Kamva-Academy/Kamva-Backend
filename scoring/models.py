from operator import mod
from django.db import models
from accounts.models import *
from django.db.models import IntegerField, Model, Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from fsm.models import Answer, Paper, Widget
from polymorphic.models import PolymorphicModel
from django.core.exceptions import ValidationError


class Deliverable(PolymorphicModel):
    class DeliverableTypes(models.TextChoices):
        Answer = 'Answer'
        Response = 'Response'

    deliverable_type = models.CharField(max_length=20, choices=DeliverableTypes.choices)
    deliverer = models.ForeignKey('accounts.User', related_name='deliverer', on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'user: {self.deliverer.username}'


class Scorable(Widget):
    class ScorableTypes(models.TextChoices):
        Problem = 'Question'
        Question = 'Problem'

    scorable_type = models.CharField(max_length=30, choices=ScorableTypes.choices)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>'


class ScoreType(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    papers = models.ManyToManyField(Paper, related_name='score_types')

    def __str__(self):
        return self.name


class ScorePackage(models.Model):
    type = models.ForeignKey(ScoreType, on_delete=models.CASCADE, related_name='score_packages')
    number = models.IntegerField(default=1)
    scorable = models.ForeignKey(Scorable, on_delete=models.CASCADE, related_name='score_packages')

    def clean(self):
        if not self.type in self.scorable.paper.score_types.all():
            raise ValidationError('selected score-type is not in the scorable\'s paper\'s score-types')
        return self

    def __str__(self):
        return f'{self.type}: {self.number}'


class Score(models.Model):
    value = IntegerField(default=0)
    type = models.ForeignKey(ScoreType, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='scores')

    class Meta:
        unique_together = ('answer', 'type')

    def __str__(self):
        return f'{self.value} × {self.score_type}'


class Comment(models.Model):
    content = models.TextField(null=False, blank=False)
    writer = models.ForeignKey('accounts.User', related_name='comments', null=True, blank=True, on_delete=models.SET_NULL)
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
        score_sum = Score.objects.filter(score_type=self.score_type, answer__submitted_by=user).aggregate(
            Sum('value')).get('value__sum', 0)
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
