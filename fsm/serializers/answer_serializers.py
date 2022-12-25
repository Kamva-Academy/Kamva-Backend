import os
from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer
from errors.error_codes import serialize_error
from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from fsm.serializers.validators import multi_choice_answer_validator


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context.get('user', None)
        validated_data.get('problem').unfinalize_older_answers(user)
        return super().create({'submitted_by': user, **validated_data})

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        if 'problem' not in validated_data.keys():
            validated_data['problem'] = instance.problem
        elif validated_data.get('problem', None) != instance.problem:
            raise ParseError(serialize_error('4102'))
        instance.problem.unfinalize_older_answers(user)
        return super(AnswerSerializer, self).update(instance, {'is_final_answer': True, **validated_data})

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        answer_sheet = self.context.get('answer_sheet', None)
        if answer_sheet is not None and problem is not None and problem.paper is not None:
            if answer_sheet.answer_sheet_of != problem.paper:
                raise ParseError(serialize_error('4027', {'problem.paper': problem.paper,
                                                          'original paper': answer_sheet.answer_sheet_of},
                                                 is_field_error=False))
        return attrs


class SmallAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'SmallAnswer', **validated_data})

    class Meta:
        model = SmallAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_solution']


class BigAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'BigAnswer', **validated_data})

    class Meta:
        model = BigAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_solution']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'problem', ]
        read_only_fields = ['id', 'problem']


class MultiChoiceAnswerSerializer(AnswerSerializer):
    choices = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all()),
                                    allow_empty=True, allow_null=False, required=True, write_only=True)

    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'choices']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_solution']

    def create(self, validated_data):
        choices = validated_data.pop('choices')

        instance = super(MultiChoiceAnswerSerializer, self).create(
            {'answer_type': 'MultiChoiceAnswer', **validated_data})
        instance.choices.add(*choices)
        instance.save()
        self.context['choices'] = choices
        return instance

    def validate(self, attrs):
        attrs = super(MultiChoiceAnswerSerializer, self).validate(attrs)
        choices = attrs.get('choices', [])
        problem = attrs.get('problem', None)
        if problem is not None:
            multi_choice_answer_validator(choices, problem.max_choices)

            for c in choices:
                if c.problem != problem:
                    raise ParseError(serialize_error(
                        '4030', is_field_error=False))

        return attrs

    def to_internal_value(self, data):
        choices = data.get('choices', [])
        choices = [c.pk if isinstance(c, Choice) else c for c in choices]
        data['choices'] = choices
        return super(MultiChoiceAnswerSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        representation = super(MultiChoiceAnswerSerializer,
                               self).to_representation(instance)
        choices = [ChoiceSerializer(c).to_representation(c)
                   for c in self.context.get('choices', [])]

        representation['choices'] = choices
        return representation


class FileAnswerSerializer(AnswerSerializer):
    upload_file_answer = serializers.PrimaryKeyRelatedField(
        queryset=UploadFileAnswer.objects.all(), required=True)

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'upload_file_answer']
        read_only_fields = ['id', 'submitted_by',
                            'created_at', 'is_solution', 'answer_file']
        write_only_fields = ['upload_file_answer']

    def validate_upload_file_answer(self, upload_file_answer):
        if upload_file_answer.submitted_by != self.context.get('user', None):
            raise ParseError(serialize_error('4049'))
        return upload_file_answer

    def validate(self, attrs):
        upload_file_answer = attrs.get('upload_file_answer', None)
        problem = attrs.get('problem', None)
        if problem:
            if upload_file_answer.problem and problem != upload_file_answer.problem:
                raise ParseError(serialize_error('4047'))
        else:
            attrs['problem'] = upload_file_answer.problem
        return super(FileAnswerSerializer, self).validate(attrs)

    def create(self, validated_data):
        problem = validated_data.get('problem', None)
        upload_file_answer = validated_data.pop('upload_file_answer', None)
        answer_sheet = validated_data.get('answer_sheet', None)
        if problem and not upload_file_answer.problem:
            upload_file_answer.problem = problem
        if answer_sheet and not upload_file_answer.answer_sheet:
            upload_file_answer.answer_sheet = answer_sheet
        upload_file_answer.save()
        return upload_file_answer

    def to_representation(self, instance):
        return UploadFileAnswerSerializer(context=self.context).to_representation(instance)


class UploadFileAnswerSerializer(AnswerSerializer):
    file_name = serializers.CharField(
        max_length=50, required=False, write_only=True)

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'file_name']
        read_only_fields = ['id', 'answer_type',
                            'submitted_by', 'created_at', 'is_solution']
        write_only_fields = ['file_name']

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        if problem:
            if problem.paper:
                if (problem.paper.since and datetime.now(problem.paper.since.tzinfo) < problem.paper.since) or \
                        (problem.paper.till and datetime.now(problem.paper.till.tzinfo) > problem.paper.till):
                    raise ParseError(serialize_error('4104'))
        return attrs

    def create(self, validated_data):
        answer_file = validated_data.get('answer_file', None)
        file_name, file_extension = os.path.splitext(answer_file.name)
        file_name = validated_data.pop('file_name', file_name)
        user = self.context.get('user', None)
        problem = validated_data.get('problem', None)
        answer_file.name = f'{file_name}_P{problem.id}_U{user.username}_T{datetime.now()}{file_extension}'
        return super(UploadFileAnswerSerializer, self).create({'answer_type': 'UploadFileAnswer', **validated_data})

    def to_representation(self, instance):
        representation = super(UploadFileAnswerSerializer,
                               self).to_representation(instance)
        answer_file = representation['answer_file']
        if answer_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['answer_file'] = domain + answer_file
        return representation


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Answer: AnswerSerializer,
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer
    }

    resource_type_field_name = 'answer_type'


class MultiChoiceSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'choices']
        read_only_fields = ['id', 'submitted_by']


class MockAnswerSerializer(serializers.Serializer):
    SmallAnswerSerializer = SmallAnswerSerializer(required=False)
    BigAnswerSerializer = BigAnswerSerializer(required=False)
    MultiChoiceAnswerSerializer = MultiChoiceAnswerSerializer(required=False)
    UploadFileAnswerSerializer = UploadFileAnswerSerializer(required=False)
