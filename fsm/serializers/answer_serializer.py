from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super().create({'submitted_by': self.context.get('user', None), **validated_data})

    # class Meta:
    #     model = Answer
    #     fields = '__all__'


class SmallAnswerSerializer(AnswerSerializer):
    class Meta:
        model = SmallAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id']


class BigAnswerSerializer(AnswerSerializer):
    class Meta:
        model = BigAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'problem', ]
        read_only_fields = ['id', 'problem']


class MultiChoiceAnswerSerializer(AnswerSerializer):
    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'choices']
        read_only_fields = ['id']


class UploadFileAnswerSerializer(AnswerSerializer):
    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'file_name']


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Answer: AnswerSerializer,
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: UploadFileAnswerSerializer
    }

    resource_type_field_name = 'answer_type'
