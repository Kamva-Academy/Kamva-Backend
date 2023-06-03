from rest_polymorphic.serializers import PolymorphicSerializer
from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from question.models import InviteeUsernameAnswer
from fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, FileAnswerSerializer
from question.serializers.invitee_username import InviteeUsernameAnswerSerializer


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer,
        InviteeUsernameAnswer: InviteeUsernameAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
