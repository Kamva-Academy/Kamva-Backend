import logging

import pytz
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta, datetime
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

from workshop_backend.settings.base import KAVENEGAR_TOKEN, SMS_CODE_DELAY, SMS_CODE_LENGTH, VOUCHER_CODE_LENGTH, \
    DISCOUNT_CODE_LENGTH

logger = logging.getLogger(__file__)


class User(AbstractUser):
    class Gender(models.TextChoices):
        Male = 'Male'
        Female = 'Female'

    phone_number = models.CharField(max_length=15, blank=False, null=False, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.CharField(max_length=300, blank=True, null=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=Gender.choices)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    national_code = models.CharField(max_length=10, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    country = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)


class EducationalInstitute(models.Model):
    class InstituteType(models.TextChoices):
        School = 'SCHOOL'
        University = 'UNIVERSITY'
        Other = 'OTHER'

    name = models.CharField(max_length=30, null=False, blank=False)
    institute_type = models.CharField(max_length=10, null=False, blank=False, choices=InstituteType.choices)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)

    date_added = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(null=True, blank=True)
    owner = models.ForeignKey(User, related_name='owned_institutes', on_delete=models.SET_NULL, null=True,
                                blank=True)
    admins = models.ManyToManyField(User, related_name='institutes', blank=True)

    def __str__(self):
        return self.name


class School(EducationalInstitute):
    class SchoolType(models.Choices):
        Elementary = 'Elementary'
        JuniorHigh = 'JuniorHigh'
        High = 'High'

    principle_name = models.CharField(max_length=30, null=True, blank=True)
    principle_phone = models.CharField(max_length=15, null=True, blank=True, unique=True)
    school_type = models.CharField(max_length=15, null=True, blank=True, choices=SchoolType.choices)


class University(EducationalInstitute):
    pass


class Studentship(models.Model):
    class StudentshipType(models.Choices):
        School = 'School'
        Academic = 'Academic'

    studentship_type = models.CharField(max_length=10, null=False, blank=False, choices=StudentshipType.choices)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_currently_studying = models.BooleanField(default=False)
    document = models.FileField(upload_to='studentship_documents/', null=True, blank=True)
    is_document_verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='studentships', on_delete=models.CASCADE, null=False)


class SchoolStudentship(Studentship):
    class Major(models.TextChoices):
        Math = 'Math'
        Biology = 'Biology'
        Literature = 'Literature'
        IslamicStudies = 'IslamicStudies'
        TechnicalTraining = 'TechnicalTraining'
        Others = 'Others'

    school = models.ForeignKey(School, related_name='students', on_delete=models.SET_NULL, null=True)
    grade = models.IntegerField(null=True, blank=True, validators=[MaxValueValidator(12), MinValueValidator(0)])
    major = models.CharField(max_length=25, null=True, blank=True, choices=Major.choices)


class AcademicStudentship(Studentship):
    class Degree(models.TextChoices):
        BA = 'BA'
        MA = 'MA'
        PHD = 'PHD'
        Postdoc = 'Postdoc'

    university = models.ForeignKey(University, related_name='academic_students', on_delete=models.SET_NULL, null=True)
    degree = models.CharField(max_length=15, null=True, blank=True, choices=Degree.choices)
    university_major = models.CharField(max_length=30, null=True, blank=True)


class Player(models.Model):
    user = models.ForeignKey(User, related_name='workshops', on_delete=models.CASCADE)
    fsm = models.ForeignKey('fsm.FSM', related_name='users', on_delete=models.CASCADE)
    purchase = models.ForeignKey('accounts.Purchase', related_name='purchase', on_delete=models.SET_NULL, null=True)
    # registration_receipt = models.ForeignKey('fsm.RegistrationReceipt', on_delete=models.SET_NULL, null=True, blank=True)
    scores = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


# class OwnableMixin(models.Model):
#     owners = models.ManyToManyField(User, related_name='owned_entities')
#
#     # TODO - work on its details
#     class Meta:
#         abstract = True


class Merchandise(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    price = models.IntegerField(default=0)
    owner = models.ForeignKey(EducationalInstitute, on_delete=models.SET_NULL, null=True, related_name='merchandises')


# class Code(models.Model):
#     TODO - create a 'code' class  and subclass discounts, vouchers & verification codes from it.
#     class CodeType(models.TextChoices):
#         DISCOUNT_CODE = 'DISCOUNT_CODE'
#         VOUCHER = 'VOUCHER'
#         VERIFICATION_CODE = 'VERIFICATION_CODE'
#
#     code_type = models.CharField(max_length=15, choices=CodeType.choices, blank=False, null=False)
#     code = models.CharField(max_length=10, null=False, blank=False)


class DiscountCodeManager(models.Manager):
    @transaction.atomic
    def create_discount_code(self, **args):
        code = User.objects.make_random_password(length=DISCOUNT_CODE_LENGTH)
        return super().create(**{'code': code, **args})


# TODO - add date validators for datetime fields
class DiscountCode(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
    expiration_date = models.DateTimeField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='discount_codes', on_delete=models.CASCADE, null=True, default=None)
    merchandise = models.ForeignKey(Merchandise, related_name='discount_codes', on_delete=models.CASCADE, null=True,
                                    default=None)

    def __str__(self):
        return self.code + " " + str(self.value)


class VoucherManager(models.Manager):
    @transaction.atomic
    def create_voucher(self, **args):
        code = User.objects.make_random_password(length=VOUCHER_CODE_LENGTH)
        return super().create(**{'remaining': args.get('amount', 0), 'code': code, **args})


class Voucher(models.Model):
    user = models.ForeignKey(User, related_name='vouchers', on_delete=models.CASCADE, null=False)
    code = models.CharField(max_length=10, null=False)
    amount = models.IntegerField(null=False)
    remaining = models.IntegerField(null=False)
    expiration_date = models.DateTimeField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)

    objects = VoucherManager()

    @transaction.atomic
    def use_on_purchase(self, purchase):
        # TODO - work on how purchase flow is.
        #  Eg. can users use a discount and a voucher or just one of them?
        if self.remaining >= purchase.merchandise.price:
            purchase.amount = max(0, purchase.amount - self.remaining)
            self.remaining -= purchase.merchandise.price
        else:
            purchase.amount = purchase.merchandise.price - self.remaining
            self.remaining = 0
        purchase.voucher = self
        purchase.save()
        self.save()


class Purchase(models.Model):
    class Status(models.TextChoices):
        Success = "Success"
        Repetitious = "Repetitious"
        Failed = "Failed"
        Started = "Started"

    ref_id = models.CharField(blank=True, max_length=100, null=True)
    amount = models.IntegerField()
    authority = models.CharField(blank=True, max_length=37, null=True)
    status = models.CharField(blank=False, choices=Status.choices, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    uniq_code = models.CharField(blank=False, max_length=100, default="")

    user = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)

    merchant = models.ForeignKey(Merchandise, related_name='purchases', on_delete=models.SET_NULL, null=True)
    voucher = models.ForeignKey(Voucher, related_name='purchases', on_delete=models.SET_NULL, null=True, default=None)
    discount_code = models.ForeignKey(DiscountCode, related_name='purchases', on_delete=models.SET_NULL, null=True,
                                      default=None)

    def __str__(self):
        return self.uniq_code


class VerificationCodeManager(models.Manager):
    @transaction.atomic
    def create_verification_code(self, phone_number, time_zone='Asia/Tehran'):
        code = User.objects.make_random_password(length=SMS_CODE_LENGTH, allowed_chars='1234567890')
        other_codes = VerificationCode.objects.filter(phone_number=phone_number, is_valid=True)
        for c in other_codes:
            c.is_valid = False
            c.save()
        verification_code = VerificationCode.objects.create(code=code, phone_number=phone_number,
                                                            expiration_date=datetime.now(pytz.timezone(time_zone))
                                                                            + timedelta(minutes=SMS_CODE_DELAY))
        return verification_code


class VerificationCode(models.Model):
    phone_number = models.CharField(blank=True, max_length=13, null=True)
    code = models.CharField(blank=True, max_length=10, null=True)
    expiration_date = models.DateTimeField(blank=False, null=False)
    is_valid = models.BooleanField(default=True)

    objects = VerificationCodeManager()

    def send_sms(self, code_type='verify'):
        api = KAVENEGAR_TOKEN
        params = {
            'receptor': self.phone_number,
            'template': code_type,
            'token': str(self.code),
            'type': 'sms'
        }
        api.verify_lookup(params)

    def __str__(self):
        return f'{self.phone_number}\'s code is: {self.code} {"+" if self.is_valid else "-"}'


# ----------------------------------------------

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
    player_type = models.CharField(max_length=10)
    score = models.IntegerField(default=0)

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
    player_type = models.CharField(max_length=10)
    score = models.IntegerField(default=0)

    # current_state = models.ForeignKey('fsm.FSMState', null=True, blank=True, on_delete=models.SET_NULL, related_name='teams')

    def __str__(self):
        s = str(self.id) + "-" + self.group_name + " ("

        for p in self.team_participants.all():
            s += str(p) + ", "
        s += ")"
        return s
