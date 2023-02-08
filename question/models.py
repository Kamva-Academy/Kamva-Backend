from django.db import models
from scoring.models import Scorable, Deliverable
from polymorphic.models import PolymorphicModel


############ QUESTIONS ############

class Question(Scorable):
    class ScorableTypes(models.TextChoices):
        InviteeUsername = 'InviteeUsername'

    text = models.TextField()
    required = models.BooleanField(default=False)
    question_type = models.CharField(max_length=30, choices=ScorableTypes.choices)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class InviteeUsernameQuestion(Question):
    pass

############ RESPONSES ############

class Response(Deliverable):
    class AnswerTypes(models.TextChoices):
        InviteeUsernameResponse = 'InviteeUsernameResponse'

    response_type = models.CharField(max_length=30, choices=AnswerTypes.choices)
    answer_sheet = models.ForeignKey('fsm.AnswerSheet', related_name='questions', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'user: {self.deliverer.username} - question: {self.question.id}'

    @property
    def question(self):
        return self.question


class InviteeUsernameResponse(Response):
    question = models.ForeignKey(InviteeUsernameQuestion, on_delete=models.CASCADE, related_name='answers')
    username = models.CharField(max_length=15)
