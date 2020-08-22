from django.db import models
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags

from enum import Enum


from collections import defaultdict

import logging
import random
import re

logger = logging.getLogger(__file__)


# Create your models here.
class Gender(Enum):
    Man = 'Man'
    Woman = 'Woman'


class Grade(Enum):
    Ten = 'ten'
    Eleven = 'eleven'
    Twelve = 'twelve'


class ParticipantStatus(Enum):
    Pending = 'Pending'
    Verified = 'Verified'
    Rejected = 'Rejected'


class Member(AbstractUser):
    is_participant = models.BooleanField(default=True)

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.username


class Participant(models.Model):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    school = models.CharField(max_length=50)
    grade = models.CharField(max_length=10, choices=[(tag.value, tag.name) for tag in Grade])
    city = models.CharField(max_length=20)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    team = models.ForeignKey('Team', models.SET_NULL,
        blank=True,null=True )

    def __str__(self):
        return str(self.member)


class Team(models.Model):
    # participants = models.ManyToManyField(Participant, blank=False)
    group_name = models.CharField(max_length=30, blank=True)
