from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer
from datetime import datetime
from errors.error_codes import serialize_error
from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from fsm.serializers.validators import multi_choice_answer_validator


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context.get('user', None)
        problem = validated_data.get('problem', None)
        answer_sheet = validated_data.get('answer_sheet', None)
        previous_answers = Answer.objects.filter(submitted_by=user, answer_sheet=answer_sheet).filter(
            Q(SmallAnswer___problem__id=problem.id) | Q(BigAnswer___problem__id=problem.id) | Q(
                UploadFileAnswer___problem__id=problem.id) | Q(MultiChoiceAnswer___problem__id=problem.id))
        for a in previous_answers:
            a.is_final_answer = False
            a.save()
        return super().create({'submitted_by': self.context.get('user', None), **validated_data})

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        answer_sheet = self.context.get('answer_sheet', None)
        if answer_sheet is not None and problem is not None and problem.paper is not None:
            if answer_sheet.answer_sheet_of != problem.paper:
                raise ParseError(serialize_error('4027', {'problem.paper': problem.paper,
                                                          'original paper': answer_sheet.answer_sheet_of},
                                                 is_field_error=False))
        return attrs

    # class Meta:
    #     model = Answer
    #     fields = '__all__'


class SmallAnswerSerializer(AnswerSerializer):
    class Meta:
        model = SmallAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_solution']


class BigAnswerSerializer(AnswerSerializer):
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

        instance = super(MultiChoiceAnswerSerializer, self).create(validated_data)
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
                    raise ParseError(serialize_error('4030', is_field_error=False))

        return attrs

    def to_internal_value(self, data):
        choices = data.get('choices', [])
        choices = [c.pk if isinstance(c, Choice) else c for c in choices]
        data['choices'] = choices
        return super(MultiChoiceAnswerSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        representation = super(MultiChoiceAnswerSerializer, self).to_representation(instance)
        choices = [ChoiceSerializer(c).to_representation(c) for c in self.context.get('choices', [])]

        representation['choices'] = choices
        return representation


class FileAnswerSerializer(AnswerSerializer):
    upload_file_answer = serializers.PrimaryKeyRelatedField(queryset=UploadFileAnswer.objects.all(), required=True)

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'upload_file_answer']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_solution', 'answer_file']
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
        return UploadFileAnswerSerializer().to_representation(instance)


class UploadFileAnswerSerializer(AnswerSerializer):
    file_name = serializers.CharField(max_length=50, required=False, write_only=True)

    def create(self, validated_data):
        answer_file = validated_data.get('answer_file', None)
        file_name = validated_data.pop('file_name', None)
        suffix = answer_file.name[answer_file.name.rfind('.'):]
        user = self.context.get('user', None)
        if file_name:
            answer_file.name = f'{file_name}-{user.username}{suffix}'
        else:
            problem = validated_data.get('problem', None)
            answer_file.name = f'Q{problem.id}-{user.username}{suffix}' if problem else f'{answer_file.name}-{user.username}{suffix}'
        return super(UploadFileAnswerSerializer, self).create({'answer_type': 'UploadFileAnswer', **validated_data})

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'file_name']
        read_only_fields = ['id', 'answer_type', 'submitted_by', 'created_at', 'is_solution']
        write_only_fields = ['file_name']


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