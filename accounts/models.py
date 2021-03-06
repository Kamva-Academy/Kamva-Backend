import logging

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



from collections import defaultdict

import logging
import random
import re

from fsm.models import *
from workshop_backend.settings.base import KAVENEGAR_TOKEN

logger = logging.getLogger(__file__)


#
# class ParticipantStatus(Enum):
#     Pending = 'Pending'
#     Verified = 'Verified'
#     Rejected = 'Rejected'


class Member(AbstractUser):
    class Grade(models.TextChoices):
        Pre = 'پیش‌ از دبستان'
        One = 'اول'
        Two = 'دوم'
        Three = 'سوم'
        four = 'چهارم'
        Five = 'پنچم'
        Six = 'ششم'
        Seven = 'هفتم'
        Eight = 'هشتم'
        Nine = 'نهم'
        Ten = 'دهم'
        Eleven = 'یازدهم'
        Twelve = 'دوازدهم'

    class Gender(models.TextChoices):
        Man = 'Man'
        Woman = 'Woman'

    is_participant = models.BooleanField(default=True)
    is_mentor = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    school = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    document = models.ImageField(upload_to='documents/', null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True,
                              choices=Gender.choices)
    grade = models.CharField(max_length=15, null=True, blank=True,
                             choices=Grade.choices)
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
    member = models.OneToOneField(Member, related_name='Mentor',
                                  on_delete=models.CASCADE)

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


class Player(models.Model):
    class PlayerType(models.TextChoices):
        TEAM = 'TEAM'
        PARTICIPANT = 'PARTICIPANT'

    player_type = models.CharField(max_length=15, choices=PlayerType.choices)
    score = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    # uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    workshops = models.ManyToManyField('fsm.FSM', through='fsm.PlayerWorkshop', related_name='players')

    def __str__(self):
        if self.player_type == self.PlayerType.TEAM:
            return str(self.team)
        elif self.player_type == self.PlayerType.PARTICIPANT:
            return str(self.participant.id) + "-" + str(self.participant)
        else:
            return "not working"


class ParticipantManager(models.Manager):

    @transaction.atomic
    def create_participant_send_sms(self, phone_number, name, *args, **kwargs):
        password = Member.objects.make_random_password(length=8, allowed_chars='RABMNT123456789')
        member = Member.objects.create_user(username=phone_number, first_name=name, password=password)
        member.is_mentor = False
        member.is_participant = True
        member.save()
        participant = Participant.objects.create(member=member, active=True,
                                                 player_type='PARTICIPANT')
        name = name.replace(" ", u"\u200B")
        participant.send_user_info_sms(
            name=name,
            username=phone_number,
            password=password,
            phone_number=phone_number
        )
        return participant, password

    @transaction.atomic
    def create_participant(self,username, name, *args, **kwargs):
        password = Member.objects.make_random_password(length=8, allowed_chars='RAST1234567890')
        member = Member.objects.create_user(username=username, first_name=name, password=password)
        member.is_mentor = False
        member.is_participant = True
        member.save()
        participant = Participant.objects.create(member=member, active=True,
                                                 player_type='PARTICIPANT')
        return participant, password


class Participant(Player):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE, primary_key=True)

    objects = ParticipantManager()

    def __str__(self):
        return str(self.member)

    def send_user_info_sms(self, name, username, password, phone_number):
        api = KAVENEGAR_TOKEN
        # params = {'sender': '10008663', 'receptor': phone_number, 'message': message}
        params = {
            'receptor': phone_number,
            'template': 'userInfo',
            'token': str(username),
            'token2': str(password),
            'token3': str(name),
            'type': 'sms'
        }
        # print(params)
        api.verify_lookup(params)


class Team(Player):
    group_name = models.CharField(max_length=30, blank=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    team_code = models.CharField(max_length=10)
    # current_state = models.ForeignKey('fsm.FSMState', null=True, blank=True, on_delete=models.SET_NULL, related_name='teams')
    team_members = models.ManyToManyField(Participant, related_name='team_set')

    def __str__(self):
        s = str(self.id) + "-" +self.group_name + " ("

        for p in self.team_members.all():
            s += str(p) + ", "
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


class VerifyCode(models.Model):
    phone_number = models.CharField(blank=True, max_length=13, null=True)
    code = models.CharField(blank=True, max_length=10, null=True)

    def send_sms(self):
        api = KAVENEGAR_TOKEN
        params = {
            'receptor': self.phone_number,
            'template': 'verify',
            'token': str(self.code),
            'type': 'sms'
        }
        api.verify_lookup(params)
