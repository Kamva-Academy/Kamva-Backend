from django.db import models
from accounts.models import EducationalInstitute, User
from django.db.models import Sum
from polymorphic.models import PolymorphicModel
from base.models import PolymorphicCreatable


class Deliverable(PolymorphicCreatable):
    class DeliverableTypes(models.TextChoices):
        Answer = 'Answer'
        Receipt = 'Receipt'

    deliverable_type = models.CharField(
        max_length=20, choices=DeliverableTypes.choices)
    deliverer = models.ForeignKey(
        'accounts.User', related_name='deliverer', on_delete=models.CASCADE)

    def __str__(self):
        return f'user: {self.deliverer.username}'


class ScoreType(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    papers = models.ManyToManyField('fsm.Paper', related_name='score_types')

    def __str__(self):
        return self.name


class Score(models.Model):
    value = models.JSONField()
    deliverable = models.ForeignKey(
        Deliverable, on_delete=models.CASCADE, related_name='scores', unique=True)
    institute = models.ForeignKey(
        EducationalInstitute, on_delete=models.CASCADE, related_name='scores', null=True)

    def __str__(self):
        return f'{self.value}'


class Comment(models.Model):
    content = models.TextField(null=False, blank=False)
    writer = models.ForeignKey('accounts.User', related_name='comments',
                               null=True, blank=True, on_delete=models.SET_NULL)
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:30]


############ CONDITION ############


class BaseCondition(PolymorphicModel):

    def evaluate(self, user: User) -> bool:
        pass


class Condition(BaseCondition):
    name = models.CharField(max_length=50, null=True, blank=True)
    amount = models.IntegerField(default=0)
    score_type = models.ForeignKey(
        ScoreType, related_name='conditions', on_delete=models.CASCADE)

    def evaluate(self, user: User) -> bool:
        score_sum = Score.objects.filter(type=self.score_type, deliverable__deliverer=user).aggregate(
            Sum('value')).get('value__sum', 0)
        return (score_sum if score_sum is not None else 0) >= self.amount

    def __str__(self):
        return f'{self.score_type.name}>={self.amount}'


class Criteria(BaseCondition):
    class Operand(models.TextChoices):
        And = "And"
        Or = "Or"

    conditions = models.ManyToManyField(
        BaseCondition, related_name='criterias')
    operand = models.CharField(
        max_length=25, blank=False, null=False, choices=Operand.choices)

    def evaluate(self, user: User) -> bool:
        result = self.operand == 'And'
        for condition in self.conditions.all():
            evaluation = condition.evaluate(user)
            result = (result and evaluation) if self.operand == 'And' else (
                result or evaluation)
        return result

    def __str__(self):
        return ('&' if self.operand == 'And' else '|').join(str(c) for c in self.conditions.all())
