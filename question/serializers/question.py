from rest_polymorphic.serializers import PolymorphicSerializer
from utils.lazy_ref import LazyRefSerializer

InviteeUsernameQuestionSerializer = LazyRefSerializer('question.serializers.invitee_username_question.InviteeUsernameQuestionSerializer')

from question.models import InviteeUsernameQuestion, Question
from scoring.serializers.score_serializers import ScorableSerializer

class QuestionSerializer(ScorableSerializer):
    pass

class QuestionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        InviteeUsernameQuestion: InviteeUsernameQuestionSerializer,
    }
