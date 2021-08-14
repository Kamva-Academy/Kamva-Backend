from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from model_utils.managers import InheritanceManager
from polymorphic.models import PolymorphicModel
from rest_framework.exceptions import PermissionDenied, ParseError

from accounts.models import *
from errors.error_codes import serialize_error
from errors.exceptions import ServiceUnavailable


class Paper(PolymorphicModel):
    class PaperType(models.TextChoices):
        RegistrationForm = "RegistrationForm"
        Article = "Article"

    paper_type = models.CharField(max_length=25, blank=False, choices=PaperType.choices)
    creator = models.ForeignKey('accounts.User', related_name='papers', null=True, blank=True,
                                on_delete=models.SET_NULL)


class AnswerSheet(PolymorphicModel):
    class AnswerSheetType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"
        FsmStateAnswerSheet = "FsmStateAnswerSheet"

    # form = models.ForeignKey(Form, null=True, default=None, on_delete=models.SET_NULL, related_name='answer_sheets')
    answer_sheet_type = models.CharField(max_length=25, blank=False, choices=AnswerSheetType.choices)

    def delete(self):
        self.answers.clear()
        return super(AnswerSheet, self).delete()


class RegistrationForm(Paper):
    class AcceptingStatus(models.TextChoices):
        AutoAccept = 'AutoAccept'
        CorrectAccept = 'CorrectAccept'
        Manual = 'Manual'

    min_grade = models.IntegerField(default=0, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = models.IntegerField(default=12, validators=[MaxValueValidator(12), MinValueValidator(0)])
    deadline = models.DateTimeField(null=True)

    # TODO - add filter for audience type

    conditions = models.TextField(null=True, blank=True)

    accepting_status = models.CharField(max_length=15, default='AutoAccept', choices=AcceptingStatus.choices)

    @property
    def event_or_fsm(self):
        try:
            if self.event:
                return self.event
        except:
            try:
                if self.fsm:
                    return self.fsm
            except:
                raise InternalServerError(serialize_error('5002'))


class RegistrationReceipt(AnswerSheet):
    class RegistrationStatus(models.TextChoices):
        Accepted = "Accepted"
        Rejected = "Rejected"
        Waiting = "Waiting"

    class CorrectionStatus(models.TextChoices):
        Correct = "Correct"
        Wrong = "Wrong"
        ManualCorrectionRequired = "ManualCorrectionRequired"
        NoCorrectionRequired = "NoCorrectionRequired"
        NoSolutionAvailable = "NoSolutionAvailable"
        Other = "Other"

    # should be in every answer sheet child
    answer_sheet_of = models.ForeignKey(RegistrationForm, related_name='registration_receipts', null=True, blank=True,
                                        on_delete=models.SET_NULL)
    user = models.ForeignKey('accounts.User', related_name='registration_receipts', on_delete=models.CASCADE,
                             null=True, blank=True)
    status = models.CharField(max_length=25, blank=False, default='Waiting', choices=RegistrationStatus.choices)

    @property
    def purchases(self):
        return self.answer_sheet_of.event_or_fsm.merchandise.purchases.filter(user=self.user)

    @property
    def is_paid(self):
        return len(self.purchases.filter(status=Purchase.Status.Success)) > 0

    class Meta:
        unique_together = ('answer_sheet_of', 'user',)

    def correction_status(self):
        for a in self.answers.all():
            if isinstance(a, (SmallAnswer, MultiChoiceAnswer)):
                correction_status = a.correction_status()
                if correction_status == self.CorrectionStatus.Wrong:
                    return self.CorrectionStatus.Wrong
                elif correction_status != self.CorrectionStatus.Correct:
                    return self.CorrectionStatus.NoCorrectionRequired
            else:
                return self.CorrectionStatus.ManualCorrectionRequired
        return self.CorrectionStatus.Correct

    def does_pass_conditions(self):
        # if exec(self.answer_sheet_of.conditions):
        #     return True
        form = self.answer_sheet_of
        studentship = self.user.studentships.filter(is_currently_studying=True).last()
        if isinstance(studentship, SchoolStudentship):
            if studentship.grade:
                if form.min_grade <= studentship.grade <= form.max_grade:
                    return True
                else:
                    raise PermissionDenied(serialize_error('4032'))
            else:
                raise ParseError(serialize_error('4033'))
        else:
            raise ParseError(serialize_error('4034'))


class Event(models.Model):
    class EventType(models.TextChoices):
        Team = 'Team'
        Individual = 'Individual'

    merchandise = models.OneToOneField('accounts.Merchandise', related_name='event', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='event', on_delete=models.SET_NULL,
                                             null=True, blank=True)
    creator = models.ForeignKey('accounts.User', related_name='events', on_delete=models.SET_NULL, null=True,
                                blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='events', on_delete=models.SET_NULL,
                               null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='events/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(max_length=40, default=EventType.Individual, choices=EventType.choices)
    team_size = models.IntegerField(default=3)
    maximum_participant = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.holder.admins.all()) if self.holder is not None else set()
        return modifiers

    @property
    def participants(self):
        if self.registration_form:
            return self.registration_form.registration_receipts.filter(is_paid=True,
                status=RegistrationReceipt.RegistrationStatus.Accepted)
        return RegistrationReceipt.objects.none()

    def delete(self, using=None, keep_parents=False):
        self.registration_form.delete() if self.registration_form is not None else None
        self.merchandise.delete() if self.merchandise is not None else None
        return super(Event, self).delete(using, keep_parents)


class FSM(models.Model):
    class FSMLearningType(models.TextChoices):
        Supervised = 'Supervised'
        Unsupervised = 'Unsupervised'

    class FSMPType(models.TextChoices):
        Team = 'Team'
        Individual = 'Individual'
        Hybrid = 'Hybrid'

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    merchandise = models.OneToOneField('accounts.Merchandise', related_name='fsm', on_delete=models.SET_NULL, null=True,
                                       blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='fsm', on_delete=models.SET_NULL, null=True,
                                             blank=True)
    creator = models.ForeignKey('accounts.User', related_name='fsms', on_delete=models.SET_NULL, null=True, blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='fsms', on_delete=models.SET_NULL,
                               null=True, blank=True)

    scores = models.JSONField(null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='workshop/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_state = models.OneToOneField('MainState', null=True, on_delete=models.SET_NULL, related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.Unsupervised,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(max_length=40, default=FSMPType.Individual, choices=FSMPType.choices)
    lock = models.CharField(max_length=10, null=True, blank=True)

    # TODO - make locks as mixins

    def __str__(self):
        return self.name

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.holder.admins.all()) if self.holder is not None else set()
        return modifiers


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
    paper = models.ForeignKey(Paper, null=True, blank=True, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    creator = models.ForeignKey('accounts.User', related_name='widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)
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
    required = models.BooleanField(default=False)

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
    problem = models.ForeignKey(MultiChoiceProblem, null=True, blank=True, on_delete=models.CASCADE,
                                related_name='choices')
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
    answer_sheet = models.ForeignKey(AnswerSheet, related_name='answers', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    submitted_by = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(null=True, blank=True)
    is_final_answer = models.BooleanField(default=False)
    is_solution = models.BooleanField(default=False)


class SmallAnswer(Answer):
    problem = models.ForeignKey('fsm.SmallAnswerProblem', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    text = models.TextField()

    def correction_status(self):
        if self.problem.solution:
            if self.text.strip() == self.problem.solution.text.strip():
                # TODO - check for semi-correct answers too
                return RegistrationReceipt.CorrectionStatus.Correct
            return RegistrationReceipt.CorrectionStatus.Wrong
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable

    def __str__(self):
        return self.text


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

    def correction_status(self):
        solution = self.problem.solution
        if solution:
            correct_choices = solution.choices.values_list(['choice'])
            for c in self.choices.values_list(['choice']):
                if c not in correct_choices:
                    return RegistrationReceipt.CorrectionStatus.Wrong
            return RegistrationReceipt.CorrectionStatus.Correct
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable

    def get_correct_choices(self):
        if self.problem.solution:
            correct_choices = set()
            for c in self.choices.values_list(['choice']):
                if c in ChoiceSelection.objects.filter(multi_choice_answer=self.problem.solution).values_list(
                        ['choice']):
                    correct_choices.add(c)
            return correct_choices
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable


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
