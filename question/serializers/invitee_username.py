from question.serializers.question import QuestionSerializer, ResponseSerializer
from question.models import InviteeUsernameQuestion, InviteeUsernameResponse


class InviteeUsernameQuestionSerializer(QuestionSerializer):

    class Meta:
        model = InviteeUsernameQuestion
        fields = ['id', 'text']


class InviteeUsernameResponseSerializer(ResponseSerializer):
    question: InviteeUsernameQuestionSerializer()

    def create(self, validated_data):
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDd")
        print(validated_data)
        return super().create({'response_type': 'InviteeUsernameResponse', **validated_data})

    class Meta:
        model = InviteeUsernameResponse
        fields = ['id', 'question', 'username']
