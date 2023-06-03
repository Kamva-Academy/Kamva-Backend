from question.serializers.question import QuestionSerializer, AnswerSerializer
from question.models import InviteeUsernameQuestion, InviteeUsernameAnswer
from scoring.models import Score
from scoring.serializers.score_serializers import ScoreSerializer
from fsm.serializers.answer_serializers import AnswerSerializer


class InviteeUsernameQuestionSerializer(QuestionSerializer):

    class Meta:
        model = InviteeUsernameQuestion
        fields = ['id', 'text']


class InviteeUsernameAnswerSerializer(AnswerSerializer):
    question: InviteeUsernameQuestionSerializer()

    def create(self, validated_data):
        username = validated_data['username']
        question = validated_data['question']
        # TODO: replace registration-receipt with invitee-username-response
        invitee_response = InviteeUsernameAnswer.objects.filter(
            deliverer__username=username, question=question).first()
        if invitee_response:
            for score_package in question.score_packages.all():
                score_type = score_package.type
                number = score_package.number
                # TODO: make a function called "change_score" and move below code to it
                score = Score.objects.filter(
                    deliverable=invitee_response, type=score_type).first()
                if score:
                    score.value = score.value + number
                    score.save()
                else:
                    serializer = ScoreSerializer(
                        data={'value': number, 'type': score_type.id, 'deliverable': invitee_response.id})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        return super().create({'response_type': 'InviteeUsernameAnswer', **validated_data})

    class Meta:
        model = InviteeUsernameAnswer
        fields = ['id', 'question', 'username']
