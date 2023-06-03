from abc import abstractmethod
from django.db import models
from fsm.models import RegistrationReceipt, State, Team
from base.models import Widget
from scoring.models import Deliverable
from django.core.validators import MinValueValidator

############ QUESTIONS ############


class Question(Widget):
    text = models.TextField()
    is_required = models.BooleanField(default=False)
    solution = models.TextField(null=True, blank=True)
    # score = models.ForeignKey(Score, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def answer(self):
        return self.answers.filter(is_correct=True).first()

    def unfinalize_older_answers(self, user):
        if isinstance(self.paper, State):
            teammates = Team.objects.get_teammates_from_widget(
                user=user, widget=self)
            older_answers = PROBLEM_ANSWER_MAPPING[self.widget_type].objects.filter(problem=self, is_final_answer=True,
                                                                                    submitted_by__in=teammates)
            for a in older_answers:
                a.is_final_answer = False
                a.save()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class ShortAnswerQuestion(Question):
    pass


class LongAnswerQuestion(Question):
    pass


class MultiChoiceQuestion(Question):
    max_choices = models.IntegerField(
        validators=[MinValueValidator(0)], default=1)


class UploadFileQuestion(Question):
    pass


class InviteeUsernameQuestion(Question):
    pass


class Choice(models.Model):
    problem = models.ForeignKey(MultiChoiceQuestion, null=True, blank=True, on_delete=models.CASCADE,
                                related_name='choices')
    text = models.TextField()

    def __str__(self):
        return self.text


############ ANSWERS ############


class Answer(Deliverable):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices)

    submitted_by = models.ForeignKey(
        'accounts.User', related_name='new_submitted_answers', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final_answer = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'user: {self.submitted_by.username if self.submitted_by else "-"} - problem {self.problem.id}'

    @abstractmethod
    def get_string_answer(self):
        pass

    @property
    def problem(self):
        return self.problem


class ShortAnswer(Answer):
    problem = models.ForeignKey('question.ShortAnswerQuestion', null=True,
                                blank=True, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()

    def correction_status(self):
        if self.problem.answer:
            if self.text.strip() == self.problem.answer.text.strip():
                # TODO - check for semi-correct answers too
                return RegistrationReceipt.CorrectionStatus.Correct
            return RegistrationReceipt.CorrectionStatus.Wrong
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable

    def get_string_answer(self):
        return self.text

    def __str__(self):
        return self.text


class LongAnswer(Answer):
    problem = models.ForeignKey('question.LongAnswerQuestion', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    text = models.TextField()

    def get_string_answer(self):
        return self.text


class ChoiceSelection(models.Model):
    multi_choice_answer = models.ForeignKey(
        'MultiChoiceAnswer', on_delete=models.CASCADE)
    choice = models.ForeignKey(
        Choice, on_delete=models.CASCADE, related_name='selections')


class MultiChoiceAnswer(Answer):
    problem = models.ForeignKey('question.MultiChoiceQuestion', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    choices = models.ManyToManyField(Choice, through=ChoiceSelection)

    def get_string_answer(self):
        # todo
        pass

    def correction_status(self):
        answer = self.problem.answer
        if answer:
            correct_choices = answer.choices.values_list(['choice'])
            for c in self.choices.values_list(['choice']):
                if c not in correct_choices:
                    return RegistrationReceipt.CorrectionStatus.Wrong
            return RegistrationReceipt.CorrectionStatus.Correct
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable

    def get_correct_choices(self):
        if self.problem.answer:
            correct_choices = set()
            for c in self.choices.values_list(['choice']):
                if c in ChoiceSelection.objects.filter(multi_choice_answer=self.problem.answer).values_list(
                        ['choice']):
                    correct_choices.add(c)
            return correct_choices
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable


class UploadFileAnswer(Answer):
    problem = models.ForeignKey('question.UploadFileQuestion', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    answer_file = models.FileField(
        upload_to='answers', max_length=4000, blank=False)

    def get_string_answer(self):
        return self.answer_file


class InviteeUsernameAnswer(Answer):
    question = models.ForeignKey(
        InviteeUsernameQuestion, on_delete=models.CASCADE, related_name='answers')
    username = models.CharField(max_length=15)


PROBLEM_ANSWER_MAPPING = {
    'ShortAnswerQuestion': ShortAnswer,
    'LongAnswerQuestion': LongAnswer,
    'MultiChoiceQuestion': MultiChoiceAnswer,
    'UploadFileQuestion': UploadFileAnswer,
}
