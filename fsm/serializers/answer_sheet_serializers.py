from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import AnswerSheet, RegistrationReceipt, Problem
from fsm.serializers.answer_serializers import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = AnswerSheet
    #     fields = ['id']
    #     read_only_fields = ['id']

    def create(self, validated_data):
        answers = validated_data.pop('answers')

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
    answers = AnswerPolymorphicSerializer(many=True)

    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_type', 'answer_sheet_of', 'answers', 'status']
        read_only_fields = ['id', 'user', 'status', 'answer_sheet_of']

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
        if answer_sheet_of.deadline and datetime.now(answer_sheet_of.deadline.tzinfo) > answer_sheet_of.deadline:
            raise ParseError(serialize_error('4036'))
        return attrs


class AnswerSheetPolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'answer_sheet_type'
    model_serializer_mapping = {
        # AnswerSheet: AnswerSheetSerializer,
        RegistrationReceipt: RegistrationReceiptSerializer,
    }
