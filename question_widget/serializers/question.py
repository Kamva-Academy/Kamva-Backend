from fsm.serializers.widget_serializers import WidgetSerializer
from scoring.serializers.score_serializers import DeliverableSerializer
from question_widget.models import Answer


class QuestionSerializer(WidgetSerializer):
    pass


class AnswerSerializer(DeliverableSerializer):

    class meta:
        model = Answer
        fields = ['id', 'name', 'paper', 'widget_type']
