from django.db import models
from apps.accounts.models import EducationalInstitute, User


# def hashem(json) -> list[tuple(int, int)]:
#     pass


# def de_hashem():
#     pass


class ScoreType(models.Model):
    name = models.CharField(max_length=50)
    institute = models.ForeignKey(
        EducationalInstitute, on_delete=models.CASCADE, related_name='score_types', null=True, blank=True)
    programs = models.ManyToManyField(
        to='fsm.Event', related_name='score_types', null=True, blank=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cost(models.Model):
    value = models.JSONField(default={})


class Reward(models.Model):
    value = models.JSONField(default={})


class Transaction(models.Model):
    value = models.JSONField(null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    to = models.ForeignKey(to=User, on_delete=models.CASCADE)


# class Comment(models.Model):
#     content = models.TextField(null=False, blank=False)
#     writer = models.ForeignKey('accounts.User', related_name='comments',
#                                null=True, blank=True, on_delete=models.SET_NULL)

#     def __str__(self):
#         return self.content[:30]


# ############ CONDITION ############


# class BaseCondition(PolymorphicModel):

#     def evaluate(self, user: User) -> bool:
#         pass


# class Condition(BaseCondition):
#     name = models.CharField(max_length=50, null=True, blank=True)
#     amount = models.IntegerField(default=0)
#     score_type = models.ForeignKey(
#         ScoreType, related_name='conditions', on_delete=models.CASCADE)

#     def evaluate(self, user: User) -> bool:
#         score_sum = Score.objects.filter(type=self.score_type, deliverable__deliverer=user).aggregate(
#             Sum('value')).get('value__sum', 0)
#         return (score_sum if score_sum is not None else 0) >= self.amount

#     def __str__(self):
#         return f'{self.score_type.name}>={self.amount}'


# class Criteria(BaseCondition):
#     class Operand(models.TextChoices):
#         And = "And"
#         Or = "Or"

#     conditions = models.ManyToManyField(
#         BaseCondition, related_name='criterias')
#     operand = models.CharField(
#         max_length=25, blank=False, null=False, choices=Operand.choices)

#     def evaluate(self, user: User) -> bool:
#         result = self.operand == 'And'
#         for condition in self.conditions.all():
#             evaluation = condition.evaluate(user)
#             result = (result and evaluation) if self.operand == 'And' else (
#                 result or evaluation)
#         return result

#     def __str__(self):
#         return ('&' if self.operand == 'And' else '|').join(str(c) for c in self.conditions.all())
