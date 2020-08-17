from django.db import models

class FSM(models.Model):
    name = models.CharField(max_length=100)

class FSMState(models.Model):
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)

class FSMEdge(models.Model):
    tail = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='inward_edges')
    priority = models.IntegerField()

class Ability(models.Model):
    edge = models.ForeignKey(FSMEdge, on_delete=models.CASCADE, related_name='abilities')
    name = models.CharField(max_length=150)
    value = models.BooleanField()

class FSMPage(models.Model):
    state = models.OneToOneField(FSMState, null=True, on_delete=models.CASCADE, unique=True, related_name='page')
    page_type = models.CharField(max_length=20)

class Widget(models.Model):
    page = models.ForeignKey(FSMEdge, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=20)
    
    class Meta:
        abstract = True

class Description(Widget):
    text = models.TextField()

class Game(Widget):
    name = models.CharField(max_length=100)
    link = models.TextField()
    answer = models.TextField()

class Answer(models.Model):
    class Meta:
        abstract = True

class SmallAnswer(Answer):
    text = models.TextField()

class BigAnswer(Answer):
    text = models.TextField()

class MultiChoiceAnswer(Answer):
    text = models.IntegerField()

class Problem(Widget):
    name = models.CharField(max_length=100)
    text = models.TextField()

    class Meta:
        abstract = True
class ProblemSmallAnswer(Problem):
    answer = models.ForeignKey(SmallAnswer, on_delete=models.CASCADE, related_name='problem')

class ProblemBigAnswer(Problem):
    answer = models.ForeignKey(BigAnswer, on_delete=models.CASCADE, related_name='problem')

class ProblemMultiChoice(Problem):
    choices = models.ListField(child=models.TextField())
    answer = models.ForeignKey(MultiChoiceAnswer, on_delete=models.CASCADE, related_name='problem')
