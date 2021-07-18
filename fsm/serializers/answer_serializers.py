from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem
from fsm.serializers.validators import multi_choice_answer_validator


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
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
        read_only_fields = ['id', 'submitted_by']


class BigAnswerSerializer(AnswerSerializer):
    class Meta:
        model = BigAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by']


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
        read_only_fields = ['id', 'submitted_by']

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


class UploadFileAnswerSerializer(AnswerSerializer):
    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'file_name']
        read_only_fields = ['id', 'submitted_by']


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Answer: AnswerSerializer,
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: UploadFileAnswerSerializer
    }

    resource_type_field_name = 'answer_type'


class MultiChoiceSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'choices']
        read_only_fields = ['id', 'submitted_by']
