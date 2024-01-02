from rest_polymorphic.serializers import PolymorphicSerializer
from apps.fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from apps.fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, FileAnswerSerializer


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
