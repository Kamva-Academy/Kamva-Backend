from django.db import models
from model_utils.managers import InheritanceManager
from polymorphic.models import PolymorphicModel

from accounts.models import *


class Paper(PolymorphicModel):
    pass


class AnswerSheet(PolymorphicModel):
    # form = models.ForeignKey(Form, null=True, default=None, on_delete=models.SET_NULL, related_name='answer_sheets')
    pass


class RegistrationForm(Paper):
    min_grade = models.IntegerField(default=0, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = models.IntegerField(default=12, validators=[MaxValueValidator(12), MinValueValidator(0)])

    conditions = models.TextField(null=True, blank=True)


class RegistrationReceipt(AnswerSheet):
    registration_form = models.ForeignKey(RegistrationForm, related_name='registration_receipts', null=True,
                                          on_delete=models.SET_NULL)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def does_pass_conditions(self):
        if exec(self.registration_form.conditions):
            return True
        return False


class Event(models.Model):
    class EventType(models.TextChoices):
        team = 'team'
        individual = 'individual'

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='events/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    event_type = models.CharField(max_length=40, default=EventType.individual,
                                  choices=EventType.choices)
    team_size = models.IntegerField(default=3)
    maximum_participant = models.IntegerField(null=True, blank=True)

    merchandise = models.OneToOneField('accounts.Merchandise', related_name='event', on_delete=models.SET_NULL,
                                       null=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='event', on_delete=models.SET_NULL,
                                             null=True)

    def __str__(self):
        return self.name


class FSM(models.Model):
    class FSMLearningType(models.TextChoices):
        withMentor = 'WITH_MENTOR'
        noMentor = 'NO_MENTOR'

    class FSMPType(models.TextChoices):
        team = 'TEAM'
        individual = 'INDIVIDUAL'
        hybrid = 'HYBRID'

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    merchandise = models.OneToOneField('accounts.Merchandise', related_name='fsm', on_delete=models.SET_NULL, null=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='fsm', on_delete=models.SET_NULL, null=True)

    scores = models.JSONField(null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='workshop/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_state = models.OneToOneField('MainState', null=True, on_delete=models.SET_NULL, related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.noMentor,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(max_length=40, default=FSMPType.individual, choices=FSMPType.choices)
    lock = models.CharField(max_length=10, null=True, blank=True)

    # TODO - make locks as mixins

    def __str__(self):
        return self.name


class FSMState(Paper):
    name = models.CharField(max_length=150)

    def __str__(self):
        try:
            state = self.mainstate
            if state.fsm:
                return '%s: %s' % (state.fsm.name, state.name)
            return self.name
        except:
            try:
                help = self.helpstate
                if help.form:
                    return '%s: %s' % (help.form.name, help.name)
                return self.name
            except:
                return self.name

    def widgets(self):
        return Widget.objects.filter(state=self)


class MainState(FSMState):
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')


class HelpState(FSMState):
    state = models.ForeignKey(MainState, on_delete=models.CASCADE, related_name='help_states')


class Article(Paper):
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='workshop/', null=True, blank=True)
    active = models.BooleanField(default=False)


# from tail to head
class FSMEdge(models.Model):
    tail = models.ForeignKey(MainState, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(MainState, on_delete=models.CASCADE, related_name='inward_edges')
    is_back_enabled = models.BooleanField(default=True)
    min_score = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    priority = models.IntegerField()
    lock = models.CharField(max_length=10, null=True, blank=True)
    has_lock = models.BooleanField(default=False)
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

    def __str__(self):
        return f'از {self.tail.name} به {self.head.name}'


class Ability(models.Model):
    edge = models.ForeignKey(FSMEdge, null=True, on_delete=models.CASCADE, related_name='abilities')
    name = models.CharField(max_length=150)
    value = models.BooleanField()
    player_history = models.ForeignKey('fsm.PlayerHistory', null=True, on_delete=models.CASCADE,
                                       related_name='abilities')

    def __str__(self):
        return self.name

    def is_valid(self, value):
        return self.value == value

    def widgets(self):
        return Widget.objects.filter(state=self)


class Widget(PolymorphicModel):
    class WidgetTypes(models.TextChoices):
        Game = 'Game'
        Video = 'Video'
        Image = 'Image'
        Description = 'Description'
        SmallAnswerProblem = 'SmallAnswerProblem'
        BigAnswerProblem = 'BigAnswerProblem'
        MultiChoiceProblem = 'MultiChoiceProblem'
        UploadFileProblem = 'UploadFileProblem'

    name = models.CharField(max_length=100, null=True)
    paper = models.ForeignKey(Paper, null=True, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    creator = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)
    duplication_of = models.ForeignKey('Widget', default=None, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='duplications')

    class Meta:
        order_with_respect_to = 'paper'


class Description(Widget):
    text = models.TextField()


class Game(Widget):
    link = models.TextField()

    def __str__(self):
        return f'{self.pk}-{self.link}'


class Video(Widget):
    link = models.TextField()

    def __str__(self):
        return self.name


class Image(Widget):
    link = models.TextField()

    def __str__(self):
        return self.name


class Problem(Widget):
    text = models.TextField(null=True, blank=True)
    help_text = models.TextField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)

    @property
    def solution(self):
        return self.answers.filter(is_solution=True).first()


class SmallAnswerProblem(Problem):
    pass


class BigAnswerProblem(Problem):
    pass


class MultiChoiceProblem(Problem):
    max_choices = models.IntegerField(validators=[MinValueValidator(0)], default=1)


class UploadFileProblem(Problem):
    pass


class Choice(models.Model):
    problem = models.ForeignKey(MultiChoiceProblem, null=True, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()

    def __str__(self):
        return self.text


class AnswerManager(InheritanceManager):
    # TODO - update for polymorphic models
    @transaction.atomic
    def create_answer(self, **args):
        user = args.get('user', None)
        problem = args.get('problem', None)
        old_answers = Answer.objects.filter(user=user).filter(problem=problem)
        for old_answer in old_answers:
            old_answer.is_final_answer = False
            old_answer.save()
        return super().create(**{'is_active': True, **{args}})


# TODO - add default answer type on answer managers
class Answer(PolymorphicModel):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices, null=False, blank=False)
    answer_sheet = models.ForeignKey(AnswerSheet, null=True, on_delete=models.SET_NULL)
    submitted_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(null=True, blank=True)
    is_final_answer = models.BooleanField(default=False)
    is_solution = models.BooleanField(default=False)


class SmallAnswer(Answer):
    problem = models.ForeignKey('fsm.SmallAnswerProblem', null=True, on_delete=models.CASCADE,
                                related_name='answers')
    text = models.TextField()


class BigAnswer(Answer):
    problem = models.ForeignKey('fsm.BigAnswerProblem', null=True, on_delete=models.CASCADE,
                                related_name='answers')
    text = models.TextField()


class ChoiceSelection(models.Model):
    multi_choice_answer = models.ForeignKey('MultiChoiceAnswer', on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='selections')


class MultiChoiceAnswer(Answer):
    problem = models.ForeignKey('fsm.MultiChoiceProblem', null=True, on_delete=models.CASCADE,
                                related_name='answers')
    choices = models.ManyToManyField(Choice, through=ChoiceSelection)


class UploadFileAnswer(Answer):
    problem = models.ForeignKey('fsm.UploadFileProblem', null=True, on_delete=models.CASCADE,
                                related_name='answers')
    answer_file = models.FileField(upload_to='AnswerFile', max_length=4000, blank=False)
    file_name = models.CharField(max_length=50)


class SubmittedAnswer(models.Model):
    player = models.ForeignKey('accounts.Player', on_delete=models.CASCADE, related_name='submitted_answers')
    publish_date = models.DateTimeField(null=True, blank=True)
    # team_history = models.ForeignKey('TeamHistory', null=True, on_delete=models.CASCADE, related_name='answers')
    answer = models.OneToOneField(Answer, null=True, on_delete=models.CASCADE, unique=True)
    problem = models.ForeignKey(Problem, null=True, on_delete=models.CASCADE, related_name='submitted_answers')

    def xanswer(self):
        try:
            return Answer.objects.filter(id=self.answer.id).first()
        except:
            return None


class PlayerWorkshop(models.Model):
    player = models.ForeignKey('accounts.Player', on_delete=models.CASCADE, related_name='player_workshop')
    workshop = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='player_workshop')
    current_state = models.ForeignKey(MainState, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='player_workshop')
    last_visit = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.id}:{str(self.player)}-{self.workshop.name}'


class PlayerHistory(models.Model):
    player_workshop = models.ForeignKey(PlayerWorkshop, on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(MainState, on_delete=models.CASCADE, related_name='player_histories')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    inward_edge = models.ForeignKey(FSMEdge, default=None, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.player_workshop.id}-{self.state.name}'
