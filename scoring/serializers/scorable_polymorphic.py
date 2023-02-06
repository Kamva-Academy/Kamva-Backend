from rest_polymorphic.serializers import PolymorphicSerializer
from question.serializers.question_polymorphic import QuestionPolymorphicSerializer
from question.models import Question

class ScorablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Question: QuestionPolymorphicSerializer,
    }