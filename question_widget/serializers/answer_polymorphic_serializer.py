from rest_polymorphic.serializers import PolymorphicSerializer
from question_widget.models import ShortAnswer, LongAnswer, MultiChoiceAnswer, UploadFileAnswer
from question_widget.models import InviteeUsernameAnswer
from question_widget.serializers.answer_serializers import ShortAnswerSerializer, LongAnswerSerializer, MultiChoiceAnswerSerializer, FileAnswerSerializer, UploadFileAnswerSerializer
from question_widget.serializers.invitee_username_question_serializer import InviteeUsernameAnswerSerializer
from rest_framework import serializers


class MockAnswerSerializer(serializers.Serializer):
    SmallAnswerSerializer = ShortAnswerSerializer(required=False)
    BigAnswerSerializer = LongAnswerSerializer(required=False)
    MultiChoiceAnswerSerializer = MultiChoiceAnswerSerializer(required=False)
    UploadFileAnswerSerializer = UploadFileAnswerSerializer(required=False)


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ShortAnswer: ShortAnswerSerializer,
        LongAnswer: LongAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer,
        InviteeUsernameAnswer: InviteeUsernameAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
