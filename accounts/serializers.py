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
from workshop_backend.settings.base import SMS_CODE_LENGTH, DISCOUNT_CODE_LENGTH
from .models import Member, Participant, Team, User, VerificationCode, EducationalInstitute, School, University, \
    SchoolStudentship, Studentship, AcademicStudentship, Merchandise, DiscountCode, Purchase
from .validators import phone_number_validator, grade_validator, price_validator

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

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        validated_data['username'] = validated_data.get('phone_number')
        instance = super().create(validated_data)
        SchoolStudentship.objects.create(user=instance, studentship_type=Studentship.StudentshipType.School)
        AcademicStudentship.objects.create(user=instance, studentship_type=Studentship.StudentshipType.Academic)
        return instance

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        instance.password = validated_data.get('password')
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'password', 'username', 'email']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'username', 'email', 'gender', 'birth_date',
                  'national_code', 'country', 'address', 'province', 'city', 'postal_code', 'profile_picture']
        read_only_fields = ['id']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, validators=[phone_number_validator])
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = str(user.id)
        return token

    def validate(self, attrs):
        credentials = {
            'password': attrs.get('password')
        }
        user = User.objects.filter(email=attrs.get('email')).first() \
               or User.objects.filter(username=attrs.get('username')).first() \
               or User.objects.filter(phone_number=attrs.get('phone_number')).first()
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

    is_approved = serializers.BooleanField(read_only=True)
    creator = serializers.PrimaryKeyRelatedField(many=False, required=False, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(many=False, required=False, read_only=True)
    admins = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)

    def create(self, validated_data):
        institute_type = validated_data.get('institute_type', None)
        if institute_type == 'School':
            return School.objects.create(**validated_data)
        elif institute_type == 'University':
            return University.objects.create(**validated_data)
        else:
            return super().create(validated_data)

    class Meta:
        model = EducationalInstitute
        fields = ['id', 'name', 'institute_type', 'address', 'province', 'city', 'postal_code', 'phone_number',
                  'contact_info', 'description', 'principal_name', 'principal_phone', 'is_approved', 'created_at',
                  'owner', 'admins', 'date_added', 'creator']
        read_only_fields = ['id', 'date_added']


class StudentshipSerializer(serializers.ModelSerializer):
    university = serializers.PrimaryKeyRelatedField(many=False, queryset=University.objects.all(), required=False)
    degree = serializers.ChoiceField(choices=AcademicStudentship.Degree.choices, required=False)
    university_major = serializers.CharField(max_length=30, required=False)

    school = serializers.PrimaryKeyRelatedField(many=False, queryset=School.objects.all(), required=False)
    grade = serializers.IntegerField(required=False, validators=[grade_validator])
    major = serializers.ChoiceField(choices=SchoolStudentship.Major.choices, required=False)

    def create(self, validated_data):
        studentship_type = validated_data.get('studentship_type', None)
        if studentship_type == Studentship.StudentshipType.School.value:
            return SchoolStudentship.objects.create(**validated_data)
        elif studentship_type == Studentship.StudentshipType.Academic.value:
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

    def to_representation(self, instance):
        representation = super(StudentshipSerializer, self).to_representation(instance)
        del representation['polymorphic_ctype']
        return representation

    class Meta:
        model = Studentship
        fields = '__all__'
        read_only_fields = ['id', 'is_document_verified', ]


# TODO - think about the AIC problem of data leak when retrieving list of profiles
class ProfileSerializer(serializers.ModelSerializer):
    school_studentship = StudentshipSerializer(read_only=True)
    academic_studentship = StudentshipSerializer(read_only=True)

    def to_representation(self, instance):
        representation = super(ProfileSerializer, self).to_representation(instance)
        del representation['password']
        return representation

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'school_studentship', 'academic_studentship', 'username', 'phone_number', 'password']


class MerchandiseSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(required=True, validators=[price_validator])
    discounted_price = serializers.IntegerField(required=False, validators=[price_validator])

    class Meta:
        model = Merchandise
        fields = '__all__'
        read_only_fields = ['id']


class DiscountCodeSerializer(serializers.ModelSerializer):
    merchandise = serializers.PrimaryKeyRelatedField(required=True, queryset=Merchandise.objects.all())
    code = serializers.CharField(max_length=DISCOUNT_CODE_LENGTH, required=False)

    def validate(self, attrs):
        code = attrs.get('code', None)
        merchandise = attrs.get('merchandise', None)

        if not merchandise:
            raise ParseError(serialize_error('4039'))
        elif not merchandise.is_active:
            raise ParseError(serialize_error('4043'))

        if code:
            discount_code = get_object_or_404(DiscountCode, code=code)

            if discount_code.user:
                user = self.context.get('user', None)
                if discount_code.user != user:
                    raise NotFound(serialize_error('4038'))

            if discount_code.merchandise:
                if merchandise != discount_code.merchandise:
                    raise ParseError(serialize_error('4040'))

            if discount_code.expiration_date and discount_code.expiration_date < datetime.now(discount_code.expiration_date.tzinfo):
                raise ParseError(serialize_error('4041'))

            if not discount_code.is_valid:
                raise ParseError(serialize_error('4042'))

        return attrs

    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['id', 'value', 'expiration_date', 'is_valid', 'user']
        extra_kwargs = {
            'code': {'validators': []}
        }


class PurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['id']



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
