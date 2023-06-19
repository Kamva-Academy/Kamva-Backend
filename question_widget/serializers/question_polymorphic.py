from rest_polymorphic.serializers import PolymorphicSerializer
from question_widget.models import InviteeUsernameQuestion
from question_widget.serializers.invitee_username import InviteeUsernameQuestionSerializer


class QuestionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        InviteeUsernameQuestion: InviteeUsernameQuestionSerializer,
    }
