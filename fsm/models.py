
from django.db import models
from model_utils.managers import InheritanceManager
from accounts.models import *


class FSM(models.Model):
    class FSMLearningType(models.TextChoices):
        withMentor = 'withMentor'
        noMentor = 'noMentor'

    class FSMPType(models.TextChoices):
        team = 'team'
        individual = 'individual'
        hybrid = 'hybrid'

    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    first_state = models.OneToOneField('FSMState', null=True, on_delete=models.SET_NULL, related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.noMentor,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(max_length=40, default=FSMPType.hybrid,
                                  choices=FSMPType.choices)

    def __str__(self):
        return self.name


class FSMState(models.Model):
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)

    def __str__(self):
        if self.fsm:
            return '%s: %s' % (self.fsm.name, self.name)
        return self.name

    def widgets(self):
        return Widget.objects.filter(state=self).select_subclasses()


class FSMEdge(models.Model):
    tail = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(FSMState, on_delete=models.CASCADE, related_name='inward_edges')
    priority = models.IntegerField()
    text = models.TextField(null=True)

    def get_next_state(self, abilities):
        output = True
        for ability in Ability.objects.filter(edge=self):
            try:
                value = abilities.filter(name=ability.name)[0].value
            except:
                output = False
                return
            output = output and ability.is_valid(value)
        return self.head if output else None


class Ability(models.Model):
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.CASCADE, related_name='abilities')
    name = models.CharField(max_length=150)
    value = models.BooleanField()
    player_history = models.ForeignKey('fsm.PlayerHistory', null=True, on_delete=models.CASCADE, related_name='abilities')

    def __str__(self):
        return self.name

    def is_valid(self, value):
        return self.value == value

    def widgets(self):
        return Widget.objects.filter(state=self).select_subclasses()


class Widget(models.Model):
    class WidgetTypes(models.TextChoices):
        Game = 'Game'
        Video = 'Video'
        Image = 'Image'
        Description = 'Description'
        ProblemSmallAnswer = 'ProblemSmallAnswer'
        ProblemBigAnswer = 'ProblemBigAnswer'
        ProblemMultiChoice = 'ProblemMultiChoice'
        ProblemUploadFileAnswer = 'ProblemUploadFileAnswer'

    state = models.ForeignKey(FSMState, null=True, on_delete=models.CASCADE, related_name='%(class)s')
    priority = models.IntegerField(default=1, null=True, blank=True)
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
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
    problem = models.OneToOneField('ProblemSmallAnswer', null=True, on_delete=models.CASCADE, unique=True,
                                   related_name='answer')
    text = models.TextField()


class BigAnswer(Answer):
    problem = models.OneToOneField('ProblemBigAnswer', null=True, on_delete=models.CASCADE, unique=True,
                                   related_name='answer')
    text = models.TextField()


class MultiChoiceAnswer(Answer):
    problem = models.OneToOneField('ProblemMultiChoice', null=True, on_delete=models.CASCADE, unique=True,
                                   related_name='answer')
    text = models.IntegerField()


class UploadFileAnswer(Answer):
    problem = models.OneToOneField('ProblemUploadFileAnswer', null=True, on_delete=models.CASCADE, unique=True,
                                   related_name='answer')
    answer_file = models.FileField(upload_to='AnswerFile', max_length=4000, blank=False)
    file_name = models.CharField(max_length=50)


class Problem(Widget):
    name = models.CharField(max_length=100, null=True)
    text = models.TextField()
    objects = InheritanceManager()


class ProblemSmallAnswer(Problem):
    pass


class ProblemBigAnswer(Problem):
    pass


class ProblemMultiChoice(Problem):
    pass


class ProblemUploadFileAnswer(Problem):
    pass


class Choice(models.Model):
    problem = models.ForeignKey(ProblemMultiChoice, null=True, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()

    def __str__(self):
        return self.text


class SubmittedAnswer(models.Model):
    player = models.ForeignKey('accounts.Player', on_delete=models.CASCADE, related_name='submited_answers')
    publish_date = models.DateTimeField(null=True, blank=True)
    # team_history = models.ForeignKey('TeamHistory', null=True, on_delete=models.CASCADE, related_name='answers')
    answer = models.OneToOneField(Answer, null=True, on_delete=models.CASCADE, unique=True)
    problem = models.ForeignKey('Problem', null=True, on_delete=models.CASCADE, related_name='submited_answers')

    def xanswer(self):
        try:
            return Answer.objects.filter(id=self.answer.id).select_subclasses()[0]
        except:
            return None


class PlayerHistory(models.Model):
    player = models.ForeignKey('accounts.Player', null=True, on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(FSMState, null=True, on_delete=models.CASCADE, related_name='player_histories')
    grade = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.player.id}-{self.state.name}'


class PlayerWorkshop (models.Model):
    player = models.ForeignKey('accounts.Player', on_delete=models.CASCADE, related_name='player_workshop')
    workshop = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='player_workshop')
    current_state = models.ForeignKey(FSMState, null=True, blank=True, on_delete=models.SET_NULL, related_name='player_workshop')
    last_visit = models.DateTimeField(null=True, blank=True)