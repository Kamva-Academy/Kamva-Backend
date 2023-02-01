from django.db import models

from fsm.models import Widget
from polymorphic.models import PolymorphicModel


############ QUESTIONS ############

class Question(Widget):
    text = models.TextField()
    required = models.BooleanField(default=False)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class InviteeUsernameQuestion(Question):
    pass

############ RESPONSES ############

class Response(PolymorphicModel):
    class AnswerTypes(models.TextChoices):
        InviteeUsernameResponse = 'InviteeUsernameResponse'

    response_type = models.CharField(max_length=30, choices=AnswerTypes.choices)
    # link to the form that the related question is
    submitted_by = models.ForeignKey('accounts.User', related_name='submitted_responses', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'user: {self.submitted_by.username if self.submitted_by else "-"} - question {self.question.id}'

    @property
    def question(self):
        return self.question


class InviteeUsernameResponse(Response):
    question = models.ForeignKey(InviteeUsernameQuestion, on_delete=models.CASCADE, related_name='answers')
    username = models.CharField(max_length=15)
