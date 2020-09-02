from django.db import models
from model_utils.managers import InheritanceManager
from accounts.models import Team, Participant

from django.db.models.signals import post_delete
from django.dispatch import receiver


class FSM(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def teams(self):
        states = FSMState.objects.filter(fsm=self)
        teams = Team.objects.filter(current_state__in=states)
        return len(teams)
    

class FSMState(models.Model):
    page = models.OneToOneField('FSMPage', null=True, on_delete=models.CASCADE, unique=True, related_name='state')
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)

    def __str__(self):
        if self.fsm:
            return '%s: %s' % (self.fsm.name, self.name)
        return self.name


class FSMEdge(models.Model):
    tail = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='inward_edges')
    priority = models.IntegerField()
    text = models.TextField(null=True)
    def get_next_state(self, abilities):
        output = True
        for ability in Ability.objects.filter(edge=self):
            try:
                value = abilities.filter(name = ability.name)[0].value
            except:
                output = False
                return
            output = output and ability.is_valid(value)
        return self.head if output else None


class Ability(models.Model):
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.CASCADE, related_name='abilities')
    name = models.CharField(max_length=150)
    value = models.BooleanField()
    team_history = models.ForeignKey('TeamHistory', null=True, on_delete=models.CASCADE, related_name='abilities')
    def __str__(self):
        return self.name

    def is_valid(self, value):
        return self.value == value


class FSMPage(models.Model):
    page_type = models.CharField(max_length=20)
    init_whiteboard = models.CharField(max_length=100000, null=True, blank=True)

    def widgets(self):
        return Widget.objects.filter(page=self).select_subclasses()


@receiver(post_delete, sender=FSMState)
def auto_delete_page_with_state(sender, instance, **kwargs):
    instance.page.delete()


class Widget(models.Model):
    page = models.ForeignKey(FSMPage, null =True, on_delete=models.CASCADE, related_name='%(class)s')
    priority = models.IntegerField()
    widget_type = models.CharField(max_length=20)
    objects = InheritanceManager()

    
class Description(Widget):
    text = models.TextField()


class Game(Widget):
    name = models.CharField(max_length=100, null=True)
    link = models.TextField()
    def __str__(self):
        return f'{self.pk}-{self.link}'

class Video(Widget):
    name = models.CharField(max_length=100, null=True)
    link = models.TextField()
    def __str__(self):
        return self.name

class Image(Widget):
    name = models.CharField(max_length=100, null=True)
    link = models.TextField()
    def __str__(self):
        return self.name


class Answer(models.Model):
    answer_type = models.CharField(max_length=20, default="Answer")
    objects = InheritanceManager()
 

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
    name = models.CharField(max_length=100, null=True)
    text = models.TextField()
    objects = InheritanceManager()

    def __str__(self):
        return self.name


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
    answer = models.OneToOneField(Answer, null=True, on_delete=models.CASCADE, unique=True)
    problem = models.ForeignKey('Problem', null=True, on_delete=models.CASCADE, related_name='submited_answers')
    
    def xanswer(self):
        try:
            return Answer.objects.filter(id=self.answer.id).select_subclasses()[0]
        except:
            return None
 

    

class TeamHistory(models.Model):
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(FSMState, null=True, on_delete=models.CASCADE, related_name='histories')
    grade = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.team.id}-{self.state.name}'
