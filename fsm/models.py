from django.db import models
from model_utils.managers import InheritanceManager
from accounts.models import Team, Participant

class FSM(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FSMState(models.Model):
    page = models.OneToOneField('FSMPage', null=True, on_delete=models.CASCADE, unique=True, related_name='state')
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class FSMEdge(models.Model):
    tail = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='inward_edges')
    priority = models.IntegerField()


class Ability(models.Model):
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.CASCADE, related_name='abilities')
    name = models.CharField(max_length=150)
    value = models.BooleanField()
    team_history = models.ForeignKey('TeamHistory', null=True, on_delete=models.CASCADE, related_name='abilities')
    def __str__(self):
        return self.name


class FSMPage(models.Model):
    page_type = models.CharField(max_length=20)

    def widgets(self):
        return Widget.objects.filter(page=self).select_subclasses()


class Widget(models.Model):
    page = models.ForeignKey(FSMPage, null =True, on_delete=models.CASCADE, related_name='%(class)s')
    priority = models.IntegerField()
    widget_type = models.CharField(max_length=20)
    objects = InheritanceManager()

    
class Description(Widget):
    text = models.TextField()


class Game(Widget):
    name = models.CharField(max_length=100)
    link = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.name


class Answer(models.Model):
    submited_answer = models.OneToOneField('SubmitedAnswer', null=True, on_delete=models.CASCADE, unique=True, related_name='%(class)s')
    class Meta:
        abstract = True


class SmallAnswer(Answer):
    problem = models.OneToOneField('ProblemSmallAnswer', null=True, on_delete=models.CASCADE, unique=True, related_name='answer')
    text = models.TextField()


class BigAnswer(Answer):
    problem = models.OneToOneField('ProblemBigAnswer', null=True, on_delete=models.CASCADE, unique=True, related_name='answer')
    text = models.TextField()


class MultiChoiceAnswer(Answer):
    problem = models.OneToOneField('ProblemMultiChoice', null=True, on_delete=models.CASCADE, unique=True, related_name='answer')
    text = models.IntegerField()


class Problem(Widget):
    name = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class ProblemSmallAnswer(Problem):
    pass


class ProblemBigAnswer(Problem):
    pass


class ProblemMultiChoice(Problem):
    pass


class Choice(models.Model):
    problem = models.ForeignKey(ProblemMultiChoice, null=True, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()

class SubmitedAnswer(models.Model):
    participant = models.ForeignKey(Participant, null=True, on_delete=models.CASCADE, related_name='submited_answers')
    publish_date = models.DateTimeField(null=True, blank=True)
    team_history = models.ForeignKey('TeamHistory', null=True, on_delete=models.CASCADE, related_name='answers')

class TeamHistory(models.Model):
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(Participant, null=True, on_delete=models.CASCADE, related_name='histories')
    grade = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    