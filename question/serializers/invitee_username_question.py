from question.serializers.question import QuestionSerializer
from question.models import InviteeUsernameQuestion

class InviteeUsernameQuestionSerializer(QuestionSerializer):

    class Meta:
        model = InviteeUsernameQuestion
        fields = ['id', 'text']
