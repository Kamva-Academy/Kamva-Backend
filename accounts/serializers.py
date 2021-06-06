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
from .models import Member, Participant, Team, User, VerificationCode, EducationalInstitute, School, University, \
    SchoolStudentship, Studentship, AcademicStudentship
from .validators import phone_number_validator, grade_validator

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
    password = serializers.CharField(write_only=True, required=False)
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
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'password', 'username', 'email', 'uuid']


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    username = serializers.CharField(required=False)
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'username', 'email', 'uuid', 'gender', 'national_code', 'birth_date',
                  'country', 'address', 'province', 'city', 'postal_code', 'profile_picture']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    password = serializers.CharField(write_only=True, required=True)
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


class InstituteSerializer(serializers.ModelSerializer):
    principal_name = serializers.CharField(max_length=30, required=False)
    principal_phone = serializers.CharField(max_length=15, validators=[phone_number_validator], required=False)
    phone_number = serializers.CharField(max_length=15, validators=[phone_number_validator], required=False)
    institute_type = serializers.ChoiceField(choices=['SCHOOL', 'UNIVERSITY', 'OTHER'])
    is_approved = serializers.BooleanField(required=False, read_only=True)
    creator = serializers.PrimaryKeyRelatedField(many=False, required=False, read_only=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)
    date_added = serializers.DateField(required=False, read_only=True)

    def create(self, validated_data):
        institute_type = validated_data.get('institute_type', None)
        if institute_type == 'SCHOOL':
            return School.objects.create(**validated_data)
        elif institute_type == 'UNIVERSITY':
            return University.objects.create(**validated_data)
        else:
            return super().create(validated_data)

    class Meta:
        model = EducationalInstitute
        fields = ['id', 'name', 'institute_type', 'address', 'province', 'city', 'postal_code', 'phone_number',
                  'contact_info', 'description', 'principal_name', 'principal_phone', 'is_approved', 'creator',
                  'owners', 'date_added', 'created_at']


class StudentshipSerializer(serializers.ModelSerializer):
    university = serializers.PrimaryKeyRelatedField(many=False, queryset=University.objects.all(), required=False)
    degree = serializers.ChoiceField(choices=['BA', 'MA', 'PHD', 'POSTDOC'], required=False)
    university_major = serializers.CharField(max_length=30, required=False)

    school = serializers.PrimaryKeyRelatedField(many=False, queryset=School.objects.all(), required=False)
    grade = serializers.IntegerField(required=False, validators=[grade_validator])
    major = serializers.ChoiceField(choices=[
        'MATH', 'BIOLOGY', 'LITERATURE', 'ISLAMIC_STUDIES', 'TECHNICAL_TRAINING', 'OTHERS'], required=False)

    def create(self, validated_data):
        studentship_type = validated_data.get('studentship_type', None)
        if studentship_type == 'SCHOOL':
            return SchoolStudentship.objects.create(**validated_data)
        elif studentship_type == 'ACADEMIC':
            return AcademicStudentship.objects.create(**validated_data)

    def validate(self, attrs):
        studentship_type = attrs.get('studentship_type', None)
        if studentship_type == 'SCHOOL':
            grade = attrs.get('grade', None)
            major = attrs.get('major', None)
            if grade:
                if 9 < grade <= 12:
                    if not major:
                        raise ParseError(serialize_error('4013'))
                elif major:
                    raise ParseError(serialize_error('4014'))
        elif studentship_type == 'ACADEMIC':
            degree = attrs.get('degree', None)
            if not degree:
                raise ParseError(serialize_error('4015'))
        return attrs

    class Meta:
        model = Studentship
        fields = ['id', 'user', 'studentship_type', 'start_date', 'end_date', 'is_currently_studying', 'document',
                  'is_document_verified', 'university', 'degree', 'university_major', 'school', 'grade', 'major']
        read_only_fields = ['is_document_verified', 'user', ]


class ProfileSerializer(serializers.ModelSerializer):
    studentships = StudentshipSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'username', 'email', 'uuid', 'gender', 'national_code', 'birth_date',
                  'country', 'address', 'province', 'city', 'postal_code', 'profile_picture', 'bio',
                  'studentships']


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
