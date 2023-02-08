from rest_polymorphic.serializers import PolymorphicSerializer
from question.models import InviteeUsernameQuestion
from question.serializers.invitee_username import InviteeUsernameQuestionSerializer

class QuestionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        InviteeUsernameQuestion: InviteeUsernameQuestionSerializer,
    }