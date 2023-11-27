import os
from datetime import datetime
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error
from apps.question_widget.models import ShortAnswer, LongAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice
from apps.fsm.serializers.validators import multi_choice_answer_validator
from apps.question_widget.serializers.base_serializers import AnswerSerializer


class ShortAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'SmallAnswer', **validated_data})

    class Meta:
        model = ShortAnswer
        fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at']


class LongAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'BigAnswer', **validated_data})

    class Meta:
        model = LongAnswer
        fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_correct']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'problem']
        read_only_fields = ['id', 'problem']


class MultiChoiceAnswerSerializer(AnswerSerializer):
    choices = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all()),
                                    allow_empty=True, allow_null=False, required=True, write_only=True)

    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'choices']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_correct']

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
        fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'answer_file', 'upload_file_answer']
        read_only_fields = ['id', 'submitted_by',
                            'created_at', 'is_correct', 'answer_file']
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
        if problem and not upload_file_answer.problem:
            upload_file_answer.problem = problem
        upload_file_answer.save()
        return upload_file_answer

    def to_representation(self, instance):
        return UploadFileAnswerSerializer(context=self.context).to_representation(instance)


class UploadFileAnswerSerializer(AnswerSerializer):
    file_name = serializers.CharField(
        max_length=50, required=False, write_only=True)

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'answer_file', 'file_name']
        read_only_fields = ['id', 'answer_type',
                            'submitted_by', 'created_at', 'is_correct']
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
