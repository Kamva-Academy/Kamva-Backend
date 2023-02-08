from rest_polymorphic.serializers import PolymorphicSerializer
from fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from question.models import InviteeUsernameResponse
from fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, FileAnswerSerializer
from question.serializers.invitee_username import InviteeUsernameResponseSerializer

class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer,
        InviteeUsernameResponse: InviteeUsernameResponseSerializer,
    }

    resource_type_field_name = 'answer_type'
