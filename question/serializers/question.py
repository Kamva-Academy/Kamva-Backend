from scoring.serializers.score_serializers import ScorableSerializer, DeliverableSerializer
from question.models import Response

class QuestionSerializer(ScorableSerializer):
    pass


class ResponseSerializer(DeliverableSerializer):
    
    def create(self, validated_data):
        user = self.context.get('user', None)
        print("!!!!!!!!!!!!!!!!!!!")
        print(validated_data)
        return super().create({'deliverer': user, **validated_data})

    class meta:
        model = Response
        fields = ['id', 'name', 'paper', 'widget_type']
