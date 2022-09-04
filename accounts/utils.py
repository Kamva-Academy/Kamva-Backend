from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError

from accounts.models import User
from errors.error_codes import serialize_error
from fsm.models import RegistrationReceipt, Team


def find_user(data):
    email = data.get('email', None)
    username = data.get('username', None)
    phone_number = data.get('phone_number', None)
    if not username:
        username = phone_number or email
        if username:
            data['username'] = username
        else:
            raise ParseError(serialize_error('4007'))

    return get_object_or_404(User, Q(username=username) | Q(phone_number=phone_number) | Q(email=email))


def find_registration_receipt(user, registration_form):
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form).first()


def create_user(**data):
    username = data.get('username', None)
    phone_number = data.get('phone_number', None)
    password = data.get('password', None)
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    gender = data.get('gender', None)

    if username is None or phone_number is None or first_name is None or last_name is None:
        raise ParseError(serialize_error('4113'))

    user = User.objects.filter(username=username).first()
    if user is None:
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=make_password(password),
            gender=gender,
        )
    if password is None:
        user.password = make_password(password)
        user.save()

    return user


def create_team(**data):
    team_name = data.get('team_name', None)
    registration_form = data.get('registration_form', None)

    if team_name is None or registration_form is None:
        raise ParseError(serialize_error('4113'))
    team = Team.objects.filter(
        name=team_name, registration_form=registration_form).first()
    if team is None:
        team = Team.objects.create(
            registration_form=registration_form)
        team.name = team_name
        team.save()

    return team
