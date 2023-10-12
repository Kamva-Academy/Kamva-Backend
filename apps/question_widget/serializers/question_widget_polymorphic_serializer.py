from rest_polymorphic.serializers import PolymorphicSerializer
from apps.question_widget.models import InviteeUsernameQuestion
from apps.question_widget.serializers.invitee_username_question_serializer import InviteeUsernameQuestionSerializer


class QuestionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        InviteeUsernameQuestion: InviteeUsernameQuestionSerializer,
    }
