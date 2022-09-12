from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError

from accounts.serializers import AccountSerializer
from accounts.models import User
from errors.error_codes import serialize_error
from fsm.models import RegistrationReceipt, Team, AnswerSheet


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


def create_or_update_user(**data):
    print("************", data)
    serializer = AccountSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    user1 = User.objects.filter(
        Q(username=validated_data.get('username'))).first()
    user2 = User.objects.filter(
        Q(phone_number=validated_data.get('phone_number'))).first()
    print(user1, user2)
    if user1 != user2:
        raise ParseError(serialize_error('4113'))
    elif user1 and user2:
        serializer.update(user1, validated_data)
        return user1
    else:
        return serializer.save()


def create_registration_receipt(user, registration_form):
    receipt = RegistrationReceipt.objects.filter(
        answer_sheet_of=registration_form, user=user).first()

    if receipt is None:
        receipt = RegistrationReceipt.objects.create(
            answer_sheet_of=registration_form,
            answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
            user=user,
            status=RegistrationReceipt.RegistrationStatus.Accepted,
            is_participating=True,
        )

    return receipt


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
