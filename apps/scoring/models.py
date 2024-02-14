from django.db import models
from apps.accounts.models import EducationalInstitute, User


class ScoreType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    institute = models.ForeignKey(
        EducationalInstitute, on_delete=models.CASCADE, related_name='score_types', null=True, blank=True)
    programs = models.ManyToManyField(
        to='fsm.Event', related_name='score_types', null=True, blank=True)
    is_public = models.BooleanField(default=False)
    icon = models.ImageField(
        upload_to='score_types_icons/', null=True, blank=True)

    def __str__(self):
        return self.name


class Cost(models.Model):
    value = models.JSONField(default={})


class Reward(models.Model):
    value = models.JSONField(default={})


class Transaction(models.Model):
    value = models.JSONField(default={})
    description = models.TextField(blank=True, null=True)
    to = models.ForeignKey(to=User, on_delete=models.CASCADE)
