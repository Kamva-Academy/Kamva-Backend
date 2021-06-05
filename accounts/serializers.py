import logging
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from errors.error_codes import serialize_error
from workshop_backend.settings.base import SMS_CODE_LENGTH
from .models import Member, Participant, Team, User, VerificationCode
from .validators import phone_number_validator

logger = logging.getLogger(__name__)


class PhoneNumberSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=True, validators=[phone_number_validator])
    code_type = serializers.ChoiceField(choices=['change_pass', 'verify'])

    def validate(self, attrs):
        if User.objects.filter(phone_number__exact=attrs.get('phone_number')).count() <= 0:
            if attrs.get('code_type') == 'change_pass':
                raise NotFound(serialize_error('4008'))
        else:
            if attrs.get('code_type') == 'verify':
                raise ParseError(serialize_error('4004', params={'param1': attrs.get('phone_number')}))

        return attrs

    class Meta:
        model = VerificationCode
        fields = ['phone_number', 'code_type']


class VerificationCodeSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=True, validators=[phone_number_validator])
    code = serializers.CharField(max_length=SMS_CODE_LENGTH, required=True)
    password = serializers.CharField(required=True)

    def validate_code(self, code):
        if len(code) < SMS_CODE_LENGTH:
            raise serializers.ValidationError(serialize_error('4002'))
        return code

    def validate(self, attrs):
        code = attrs.get("code", None)
        phone_number = attrs.get("phone_number", None)
        verification_code = VerificationCode.objects.filter(phone_number=phone_number, code=code, is_valid=True).first()

        if not verification_code:
            raise ParseError(serialize_error('4003'))

        if datetime.now(verification_code.expiration_date.tzinfo) > verification_code.expiration_date:
            raise ParseError(serialize_error('4005'))

        return attrs

    class Meta:
        model = VerificationCode
        fields = ['phone_number', 'code', 'password']


class AccountSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False)
    id = serializers.ReadOnlyField()

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        validated_data['username'] = validated_data.get('phone_number')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        instance.password = validated_data.get('password')
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'password', 'username', 'email', 'uuid']


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    username = serializers.CharField(required=False)
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'username', 'email', 'uuid', 'gender', 'national_code', 'birth_date',
                  'country', 'address', 'province', 'city', 'postal_code']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['uuid'] = str(user.uuid)
        return token

    def validate(self, attrs):
        credentials = {
            'password': attrs.get("password")
        }
        user = User.objects.filter(email=attrs.get("email")).first() \
               or User.objects.filter(username=attrs.get("username")).first() \
               or User.objects.filter(phone_number=attrs.get("phone_number")).first()
        if user:
            credentials['username'] = user.username
            try:
                return super().validate(credentials)
            except:
                raise AuthenticationFailed(serialize_error('4009'))
        else:
            raise AuthenticationFailed(serialize_error('4006'))


#
# class MemberSerializer(serializers.ModelSerializer):
#     """
#     Currently unused in preference of the below.
#     """
#     email = serializers.EmailField(
#         required=True
#     )
#     username = serializers.CharField()
#     password = serializers.CharField(min_length=8, write_only=True)
#
#     class Meta:
#         model = Member
#         fields = ('email', 'username', 'password')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         password = validated_data.pop('password', None)
#         instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         return instance


class ParticipantsListField(serializers.RelatedField):
    def to_representation(self, value):
        return value.member.first_name


class TeamSerializer(serializers.ModelSerializer):
    # histories = TeamHistorySerializer(many=True)
    # p_type = serializers.Field(source="team")
    team_participants = ParticipantsListField(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['player_type', 'id', 'uuid', 'group_name', 'score', 'team_participants']


class PlayerSerializer(serializers.Serializer):
    @classmethod
    def get_serializer(cls, model):
        try:
            model.team
            return TeamSerializer
        except:
            return ParticipantSerializer

    def to_representation(self, instance):
        try:
            instance.team
            serializer = TeamSerializer
            return serializer(instance.team).data
        except:
            try:
                instance.participant
                serializer = ParticipantSerializer
                return serializer(instance.participant).data
            except:
                return {}


class ParticipantSerializer(serializers.Serializer):
    # player_type = serializers.CharField(source='player_type()', read_only=True)
    # customField = serializers.Field(source='get_absolute_url')
    class Meta:
        model = Participant

    def to_representation(self, instance):
        return {
            'player_type': instance.player_type,
            'name': instance.member.first_name,
            'id': instance.id,
            'score': instance.score,
            'uuid': instance.member.uuid
        }
