from django.db import models
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.tokens import account_activation_token
import uuid

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
    is_mentor = models.BooleanField(default=False)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def send_signup_email(self, base_url, password=''):
        options = {
            'user': self,
            'base_url': base_url,
            'token': account_activation_token.make_token(self),
            'uid': urlsafe_base64_encode(force_bytes(self.pk))
        }
        if password != '':
            options['password'] = password
        if self.participant.team is not None:
            options['team'] = self.participant.team.id

        html_content = strip_spaces_between_tags(render_to_string('auth/signup_email.html', options))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)
        msg = EmailMultiAlternatives('تایید ثبت‌نام اولیه', text_content, 'Rastaiha <info@rastaiha.ir>', [self.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.username


class MentorManager(models.Manager):
    @transaction.atomic
    def create_mentor(self, email, password, *args, **kwargs):

        member = Member.objects.create_user(username=email, email=email, password=password)
        member.is_mentor = True
        member.is_participant = False
        member.save()
        mentor = Mentor.objects.create(member=member)
        return mentor


class Mentor(models.Model):
    objects = MentorManager()
    member = models.OneToOneField(Member, related_name='Mentor', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member)

    def send_greeting_email(self, username, password):
        html_content = strip_spaces_between_tags(render_to_string('auth/mentor_greet_email.html', {
            'login_url': 'rastaiha.ir/login' ,
            'username': username,
            'password': password
        }))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)

        msg = EmailMultiAlternatives('اطلاعات کاربری منتور', text_content, 'Rastaiha <info@rastaiha.ir>', [username])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class Participant(models.Model):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE, primary_key=True)
    school = models.CharField(max_length=50)
    grade = models.CharField(max_length=10, choices=[(tag.value, tag.name) for tag in Grade])
    city = models.CharField(max_length=20)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    team = models.ForeignKey('Team', models.SET_NULL,
        blank=True, null=True)
    accepted = models.BooleanField(default=False)
    ent_answer = models.FileField(blank=True, null=True, upload_to='ent_answers')

    def __str__(self):
        return str(self.member)


class Team(models.Model):
    group_name = models.CharField(max_length=30, blank=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=False)
    current_state = models.ForeignKey('fsm.FSMState', null=True, on_delete=models.SET_NULL, related_name='teams')
    def __str__(self):
        s = str(self.id) + "-" +self.group_name + " ("

        for p in self.participant_set.all():
            s+= str(p) + ", "
        s += ")"
        return s


class Payment(models.Model):
    STATUS_CHOICE = (
        ("SUCCESS", "SUCCESS"),
        ("REPETITIOUS", "REPETITIOUS"),
        ("FAILED", "FAILED"),
    )

    user = models.ForeignKey(Participant, on_delete=models.CASCADE)
    ref_id = models.CharField(blank=True, max_length=100, null=True)
    amount = models.IntegerField()
    authority = models.CharField(blank=False, max_length=37, null=False)
    status = models.CharField(blank=False, choices=STATUS_CHOICE, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    uniq_code = models.CharField(blank=False, max_length=100, default="")

    def __str__(self):
        return self.uniq_code
