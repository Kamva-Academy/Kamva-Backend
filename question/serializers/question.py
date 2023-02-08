from scoring.serializers.score_serializers import ScorableSerializer, DeliverableSerializer
from question.models import Response

class QuestionSerializer(ScorableSerializer):
    pass


class ResponseSerializer(DeliverableSerializer):
    
    class meta:
        model = Response
        fields = ['id', 'name', 'paper', 'widget_type']
