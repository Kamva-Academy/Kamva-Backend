from rest_polymorphic.serializers import PolymorphicSerializer
from apps.fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from apps.question_widget.models import InviteeUsernameAnswer
from apps.fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, FileAnswerSerializer
from apps.question_widget.serializers.invitee_username_question_serializer import InviteeUsernameAnswerSerializer


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: FileAnswerSerializer,
        InviteeUsernameAnswer: InviteeUsernameAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
