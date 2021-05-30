import logging

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
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


class User(AbstractUser):
    class Gender(models.TextChoices):
        Man = 'Man'
        Woman = 'Woman'

    phone_number = models.CharField(max_length=15, blank=False, null=False, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=Gender.choices)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    national_code = models.CharField(max_length=10, null=True, blank=True)

    country = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)


class EducationalInstitute(models.Model):
    class InstituteType(models.TextChoices):
        School = 'SCHOOL'
        University = 'UNIVERSITY'
        Other = 'Other'

    name = models.CharField(max_length=30, null=False, blank=False)
    type = models.CharField(max_length=10, null=False, blank=False, choices=InstituteType.choices)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)


class School(EducationalInstitute):
    principle_name = models.CharField(max_length=30, null=True, blank=True)
    principle_phone = models.CharField(max_length=15, null=True, blank=True, unique=True)


class University(EducationalInstitute):
    pass


class Student(models.Model):
    class Grade(models.TextChoices):
        Pre = 'PRE'
        One = 'ONE'
        Two = 'TWO'
        Three = 'THREE'
        Four = 'FOUR'
        Five = 'FIVE'
        Six = 'SIX'
        Seven = 'SEVEN'
        Eight = 'EIGHT'
        Nine = 'NINE'
        Ten = 'TEN'
        Eleven = 'ELEVEN'
        Twelve = 'TWELVE'

    class Major(models.TextChoices):
        Math = 'MATH'
        Biology = 'BIOLOGY'
        Literature = 'LITERATURE'
        IslamicStudies = 'ISLAMIC_STUDIES'
        TechnicalTraining = 'TECHNICAL_TRAINING'
        Others = 'Others'

    user = models.OneToOneField(User, related_name='student', on_delete=models.CASCADE, null=False)
    school = models.ForeignKey(School, related_name='students', on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to='school_documents/', null=True, blank=True)
    grade = models.CharField(max_length=15, null=True, blank=True, choices=Grade.choices)
    major = models.CharField(max_length=25, null=True, blank=True, choices=Major.choices)


class CollegeStudent(models.Model):
    class Degree(models.TextChoices):
        BA = 'BA'
        MA = 'MA'
        PHD = 'PHD'
        Postdoc = 'POSTDOC'

    user = models.OneToOneField(User, related_name='college_student', on_delete=models.CASCADE, null=False)
    university = models.ForeignKey(School, related_name='college_students', on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to='college_documents/', null=True, blank=True)
    degree = models.CharField(max_length=15, null=True, blank=True, choices=Degree.choices)
    major = models.CharField(max_length=30, null=True, blank=True)


class MemberManager(BaseUserManager):
    pass


class Member(AbstractBaseUser):

    objects = MemberManager()
    username = models.CharField(unique=True, max_length=15, blank=True, null=True)
    is_participant = models.BooleanField(default=True)
    is_mentor = models.BooleanField(default=False)
    is_event_owner = models.BooleanField(default=False)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=15, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    school = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True,
                              default='Male')
    grade = models.CharField(max_length=15, null=True, blank=True,
                             default='ONE')
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    is_anonymous = False
    is_authenticated = False

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


class EventOwnerManager(models.Manager):
    @transaction.atomic
    def create_event_owner(self, email, password, *args, **kwargs):
        member = Member.objects.create_user(username=email, email=email, password=password)
        member.is_mentor = True
        member.is_event_owner = True
        member.is_participant = False
        member.save()
        mentor = Mentor.objects.create(member=member)
        event_owner = EventOwner.objects.create(member=member)
        return event_owner


class EventOwner(models.Model):
    objects = EventOwnerManager()
    member = models.OneToOneField(Member, related_name='owner',
                                  on_delete=models.CASCADE)
    events = models.ManyToManyField('fsm.Event', related_name='event_owners')

    def __str__(self):
        return str(self.member)


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
    member = models.OneToOneField(Member, related_name='mentor',
                                  on_delete=models.CASCADE)
    workshops = models.ManyToManyField('fsm.FSM', related_name='workshop_mentors')

    def __str__(self):
        return str(self.member)

    def send_greeting_email(self, username, password):
        html_content = strip_spaces_between_tags(render_to_string('auth/mentor_greet_email.html', {
            'login_url': 'zero.rastaiha.ir',
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
    # workshops = models.ManyToManyField('fsm.FSM', through='fsm.PlayerWorkshop', related_name='workshop_players')
    event = models.ForeignKey('fsm.Event', related_name='event_players',
                              on_delete=models.CASCADE, null=True, blank=False)

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
    def create_participant(self, username, name, *args, **kwargs):
        password = Member.objects.make_random_password(length=8, allowed_chars='RAST1234567890')
        member = Member.objects.create_user(username=username, first_name=name, password=password)
        member.is_mentor = False
        member.is_participant = True
        member.save()
        participant = Participant.objects.create(member=member, active=True,
                                                 player_type='PARTICIPANT')
        return participant, password


# member's participation in event
class Participant(Player):
    member = models.ForeignKey(Member, related_name='event_participant', on_delete=models.CASCADE)
    event_team = models.ForeignKey('Team', related_name='team_participants',
                                   null=True, blank=True, on_delete=models.CASCADE)
    # TODO change file directory to event name
    selection_doc = models.FileField(upload_to='selection_answers/', null=True, blank=True)
    is_paid = models.BooleanField(default=False)  # پرداخت
    is_accepted = models.BooleanField(default=False)  # برای گزینش
    is_participated = models.BooleanField(default=False)  # شرکت‌کنند‌های نهایی رویداد

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
    group_name = models.CharField(max_length=200, blank=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    team_code = models.CharField(max_length=10)

    # current_state = models.ForeignKey('fsm.FSMState', null=True, blank=True, on_delete=models.SET_NULL, related_name='teams')

    def __str__(self):
        s = str(self.id) + "-" + self.group_name + " ("

        for p in self.team_participants.all():
            s += str(p) + ", "
        s += ")"
        return s


class Payment(models.Model):
    STATUS_CHOICE = (
        ("SUCCESS", "SUCCESS"),
        ("REPETITIOUS", "REPETITIOUS"),
        ("FAILED", "FAILED"),
        ("STARTED", "STARTED"),
    )

    # TODO - add discount, discount from front is bS
    participant = models.ForeignKey(Participant, related_name="participant_payment", on_delete=models.CASCADE)
    ref_id = models.CharField(blank=True, max_length=100, null=True)
    amount = models.IntegerField()
    authority = models.CharField(blank=True, max_length=37, null=True)
    status = models.CharField(blank=False, choices=STATUS_CHOICE, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    uniq_code = models.CharField(blank=False, max_length=100, default="")
    discount_code = models.ForeignKey('accounts.DiscountCode', related_name="payments", on_delete=models.CASCADE,
                                      null=True)

    def __str__(self):
        return self.uniq_code


class DiscountCode(models.Model):
    participant = models.ForeignKey(Participant, related_name='participant_discount_code', on_delete=models.CASCADE)
    code = models.CharField(blank=True, max_length=10, null=False)
    value = models.FloatField(null=False, blank=False)
    expiration_date = models.DateTimeField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.participant) + " " + self.code + " " + str(self.value)


class VerifyCode(models.Model):
    phone_number = models.CharField(blank=True, max_length=13, null=True)
    code = models.CharField(blank=True, max_length=10, null=True)
    expiration_date = models.DateTimeField(blank=False, null=False)
    is_valid = models.BooleanField(default=True)

    def send_sms(self, type='verify'):
        api = KAVENEGAR_TOKEN
        params = {
            'receptor': self.phone_number,
            'template': type,  # 'verify' if type != 'changePass' else 'changePass',
            'token': str(self.code),
            'type': 'sms'
        }
        api.verify_lookup(params)
