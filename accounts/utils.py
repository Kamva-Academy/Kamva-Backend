from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError

from accounts.serializers import AccountSerializer
from accounts.models import User
from errors.error_codes import serialize_error
from fsm.models import RegistrationForm, RegistrationReceipt, Team, AnswerSheet
from fsm.serializers.answer_sheet_serializers import MyRegistrationReceiptSerializer


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

    return get_object_or_404(User, username=username)


def find_registration_receipt(user, registration_form):
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form).first()


def update_or_create_user_account(**user_data):
    # hande name
    if not user_data.get('first_name') and not user_data.get('last_name') and user_data.get('full_name'):
        full_name_parts = user_data['full_name'].split(' ')
        user_data['first_name'] = full_name_parts[0]
        user_data['last_name'] = ' '.join(full_name_parts[1:])

    serializer = AccountSerializer(data=user_data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    user_account = None
    if validated_data.get('username'):
        user_account = User.objects.filter(
            username=validated_data.get('username')).first()
    elif validated_data.get('phone_number'):
        user_account = User.objects.filter(
            phone_number=validated_data.get('phone_number')).first()
    elif validated_data.get('national_code'):
        user_account = User.objects.filter(
            national_code=validated_data.get('national_code')).first()
    if user_account:
        # if user exists, dont change his/her account
        return user_account
    else:
        return serializer.save()


def update_or_create_registration_receipt(user: User, registration_form: RegistrationForm):
    serializer = MyRegistrationReceiptSerializer(data={
        'answer_sheet_of': registration_form.id,
        'answer_sheet_type': AnswerSheet.AnswerSheetType.RegistrationReceipt,
        'user': user.id,
        'status': RegistrationReceipt.RegistrationStatus.Accepted,
        'is_participating': True,
    })
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    receipt = RegistrationReceipt.objects.filter(
        user=user, answer_sheet_of=registration_form).first()
    if receipt:
        return serializer.update(receipt, validated_data)
    else:
        return serializer.save()


def update_or_create_team(participant_group_name: str, chat_room_link: str, receipt: RegistrationReceipt, registration_form: RegistrationForm):
    if not participant_group_name:
        return
    participant_group = create_team(team_name=participant_group_name,
                                    registration_form=registration_form)
    team_with_same_head = Team.objects.filter(
        team_head=receipt).first()
    if team_with_same_head:
        team_with_same_head.team_head = None
        team_with_same_head.save()
    if not participant_group.team_head:
        participant_group.team_head = receipt
    if chat_room_link:
        participant_group.chat_room = chat_room_link
    participant_group.save()
    receipt.team = participant_group
    receipt.save()


def create_team(**data):
    team_name = data.get('team_name', None)
    registration_form = data.get('registration_form', None)

    if not team_name or not registration_form:
        raise ParseError(serialize_error('4113'))
    team = Team.objects.filter(
        name=team_name, registration_form=registration_form).first()
    if not team:
        team = Team.objects.create(
            registration_form=registration_form)
        team.name = team_name
        team.save()

    return team
