from rest_polymorphic.serializers import PolymorphicSerializer
from question_widget.models import InviteeUsernameQuestion
from question_widget.serializers.question_widget_serializers import InviteeUsernameQuestionSerializer


class QuestionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        InviteeUsernameQuestion: InviteeUsernameQuestionSerializer,
    }
