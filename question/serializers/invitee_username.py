from question.serializers.question import QuestionSerializer, ResponseSerializer
from question.models import InviteeUsernameQuestion, InviteeUsernameResponse
from scoring.serializers.score_serializers import ScoreSerializer
from fsm.serializers.answer_serializers import AnswerSerializer

class InviteeUsernameQuestionSerializer(QuestionSerializer):

    class Meta:
        model = InviteeUsernameQuestion
        fields = ['id', 'text']


class InviteeUsernameResponseSerializer(ResponseSerializer):
    question: InviteeUsernameQuestionSerializer()

    def create(self, validated_data):
        username = validated_data['username']
        question = validated_data['question']
        score_packages = question.score_packages.all()
        response = super().create({'response_type': 'InviteeUsernameResponse', **validated_data})
        for score_package in score_packages:
            score_type = score_package.type
            number = score_package.number
            serializer = ScoreSerializer(data={'value':number, 'type': score_type, 'deliverable': response})
            if serializer.is_valid():
                serializer.save()
        return response

    class Meta:
        model = InviteeUsernameResponse
        fields = ['id', 'question', 'username']
