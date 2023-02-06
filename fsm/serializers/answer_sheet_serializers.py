from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from accounts.serializers import StudentshipSerializer
from errors.error_codes import serialize_error
from fsm.models import AnswerSheet, RegistrationReceipt, Problem
from fsm.serializers.answer_serializers import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = AnswerSheet
    #     fields = ['id']
    #     read_only_fields = ['id']

    def create(self, validated_data):
        answers = validated_data.pop('answers') if 'answers' in validated_data.keys() else []
        instance = super(AnswerSheetSerializer, self).create(validated_data)
        context = self.context
        context['answer_sheet'] = instance
        for a in answers:
            serializer = AnswerPolymorphicSerializer(data=a, context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['answer_sheet'] = instance
                serializer.save()

        return instance

    def validate(self, attrs):
        answers = attrs.get('answers', [])
        problems = [a.get('problem', None) for a in answers]
        paper = self.context.get('answer_sheet_of', None)
        if paper is not None:
            for w in paper.widgets.all():
                if isinstance(w, Problem):
                    if w.required and w not in problems:
                        raise ParseError(serialize_error('4029', {'problem': w}))

        return attrs


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    answers = AnswerPolymorphicSerializer(many=True, required=False)

    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_type', 'answer_sheet_of', 'answers', 'status', 'is_participating', 'team',
                  'certificate']
        read_only_fields = ['id', 'user', 'status', 'answer_sheet_of', 'is_participating', 'team', 'certificate']

    def create(self, validated_data):
        return super(RegistrationReceiptSerializer, self).create({'user': self.context.get('user', None),
                                                                  **validated_data})

    def validate(self, attrs):
        attrs = super(RegistrationReceiptSerializer, self).validate(attrs)
        user = self.context.get('user', None)
        answer_sheet_of = self.context.get('answer_sheet_of', None)

        if user is not None and answer_sheet_of is not None:
            if len(RegistrationReceipt.objects.filter(answer_sheet_of=answer_sheet_of, user=user)) > 0:
                raise ParseError(serialize_error('4028'))
        return attrs


class RegistrationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_type', 'answer_sheet_of', 'status', 'is_participating', 'team',
                  'certificate']
        read_only_fields = ['id', 'user', 'answer_sheet_type', 'answer_sheet_of', 'status', 'is_participating', 'team',
                            'certificate']

    def to_representation(self, instance):
        representation = super(RegistrationInfoSerializer, self).to_representation(instance)
        user = instance.user
        representation['first_name'] = user.first_name
        representation['last_name'] = user.last_name
        representation['username'] = user.username
        representation['profile_picture'] = user.profile_picture.url if user.profile_picture else None
        if representation['profile_picture'] is not None and representation['profile_picture'].startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['profile_picture'] = domain + representation['profile_picture']
        representation['school_studentship'] = StudentshipSerializer().to_representation(user.school_studentship) if getattr(user, 'school_studentship') else None
        representation['academic_studentship'] = StudentshipSerializer().to_representation(user.academic_studentship) if getattr(user, 'academic_studentship') else None
        return representation


class AnswerSheetPolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'answer_sheet_type'
    model_serializer_mapping = {
        # AnswerSheet: AnswerSheetSerializer,
        RegistrationReceipt: RegistrationReceiptSerializer,
    }


class RegistrationPerCitySerializer(serializers.Serializer):
    city = serializers.CharField(max_length=50)
    registration_count = serializers.IntegerField(min_value=0)


class RegistrationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RegistrationReceipt.RegistrationStatus.choices)


class ReceiptGetSerializer(serializers.Serializer):
    receipt = serializers.PrimaryKeyRelatedField(queryset=RegistrationReceipt.objects.filter(is_participating=True),
                                                 required=True)
