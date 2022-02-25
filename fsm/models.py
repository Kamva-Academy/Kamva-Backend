from re import search
from rest_framework.exceptions import PermissionDenied, ParseError

from accounts.models import *
from errors.error_codes import serialize_error


class Paper(PolymorphicModel):
    class PaperType(models.TextChoices):
        RegistrationForm = 'RegistrationForm'
        State = 'State'
        Hint = 'Hint'
        Article = 'Article'

    paper_type = models.CharField(max_length=25, blank=False, choices=PaperType.choices)
    creator = models.ForeignKey('accounts.User', related_name='papers', null=True, blank=True,
                                on_delete=models.SET_NULL)
    since = models.DateTimeField(null=True, blank=True)
    till = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, default=None)
    is_exam = models.BooleanField(default=False)

    def delete(self):
        for w in Widget.objects.filter(paper=self):
            try:
                w.delete()
            except:
                w.paper = None
                w.save()
        return super(Paper, self).delete()

    def __str__(self):
        return f"{self.paper_type}"


class AnswerSheet(PolymorphicModel):
    class AnswerSheetType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"
        StateAnswerSheet = "StateAnswerSheet"

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

    class GenderPartitionStatus(models.TextChoices):
        OnlyMale = 'OnlyMale'
        OnlyFemale = 'OnlyFemale'
        BothPartitioned = 'BothPartitioned'
        BothNonPartitioned = 'BothNonPartitioned'

    class RegisterPermissionStatus(models.TextChoices):
        DeadlineMissed = "DeadlineMissed"
        NotStarted = "NotStarted"
        StudentshipDataIncomplete = "StudentshipDataIncomplete"
        NotPermitted = "NotPermitted"
        GradeNotAvailable = "GradeNotAvailable"
        StudentshipDataNotApproved = "StudentshipDataNotApproved"
        Permitted = "Permitted"

    class AudienceType(models.TextChoices):
        Student = 'Student'
        Academic = 'Academic'
        All = 'All'

    min_grade = models.IntegerField(default=0, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = models.IntegerField(default=12, validators=[MaxValueValidator(12), MinValueValidator(0)])

    # TODO - add filter for audience type

    conditions = models.TextField(null=True, blank=True)

    accepting_status = models.CharField(max_length=15, default='AutoAccept', choices=AcceptingStatus.choices)
    gender_partition_status = models.CharField(max_length=25, default='BothPartitioned',
                                               choices=GenderPartitionStatus.choices)
    audience_type = models.CharField(max_length=50, default='Student', choices=AudienceType.choices)

    has_certificate = models.BooleanField(default=True)
    certificates_ready = models.BooleanField(default=False)

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
                return None

    def user_permission_status(self, user):
        check_time(self)

        # if exec(self.answer_sheet_of.conditions):
        #     return True
        # TODO - handle for academic studentship too
        if self.audience_type == self.AudienceType.Academic:
            studentship = user.academic_studentship
            if studentship:
                if not studentship.university:
                    return self.RegisterPermissionStatus.StudentshipDataIncomplete
            else:
                return self.RegisterPermissionStatus.StudentshipDataNotApproved
        elif self.audience_type == self.AudienceType.Student:
            studentship = user.school_studentship
            if studentship:
                if studentship.grade:
                    if self.min_grade <= studentship.grade <= self.max_grade:
                        if studentship.school is not None or studentship.document is not None:

                            return self.RegisterPermissionStatus.Permitted
                        else:
                            return self.RegisterPermissionStatus.StudentshipDataIncomplete
                    else:
                        return self.RegisterPermissionStatus.NotPermitted
                else:
                    return self.RegisterPermissionStatus.GradeNotAvailable
            else:
                return self.RegisterPermissionStatus.StudentshipDataNotApproved
        return self.RegisterPermissionStatus.Permitted

    def check_time(self):
        if self.till and datetime.now(self.till.tzinfo) > self.till:
            return self.RegisterPermissionStatus.DeadlineMissed
        if self.since and datetime.now(self.since.tzinfo) < self.since:
            return self.RegisterPermissionStatus.NotStarted

    def __str__(self):
        return f'<{self.id}-{self.paper_type}>:{self.event_or_fsm.name if self.event_or_fsm else None}'


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
    is_participating = models.BooleanField(default=False)
    team = models.ForeignKey('fsm.Team', on_delete=models.SET_NULL, related_name='members', null=True, blank=True)
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True, default=None)

    @property
    def purchases(self):
        if self.answer_sheet_of.event_or_fsm.merchandise:
            return self.answer_sheet_of.event_or_fsm.merchandise.purchases.filter(user=self.user)
        return Purchase.objects.none()

    @property
    def is_paid(self):
        return len(self.purchases.filter(
            status=Purchase.Status.Success)) > 0 if self.answer_sheet_of.event_or_fsm.merchandise else True

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

    def __str__(self):
        return f'{self.id}:{self.user.full_name}{"+" if self.is_participating else "x"}'


class TeamManager(models.Manager):

    def get_team_from_widget(self, user, widget):
        form = widget.paper.fsm.registration_form or widget.paper.fsm.event.registration_form
        return Team.objects.filter(registration_form=form, members__user=user).first()

    def get_teammates_from_widget(self, user, widget):
        team = self.get_team_from_widget(user, widget)
        return team.members.values_list('user', flat=True) if team is not None else [user]


class Team(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    registration_form = models.ForeignKey(RegistrationForm, related_name='teams', null=True, blank=True,
                                          on_delete=models.SET_NULL)
    team_head = models.OneToOneField(RegistrationReceipt, related_name='headed_team', null=True, blank=True,
                                     on_delete=models.SET_NULL)

    objects = TeamManager()

    def __str__(self):
        return f'{self.name}:{",".join(member.user.full_name for member in self.members.all())}'


class Invitation(models.Model):
    class InvitationStatus(models.TextChoices):
        Waiting = "Waiting"
        Rejected = "Rejected"
        Accepted = "Accepted"

    invitee = models.ForeignKey(RegistrationReceipt, on_delete=models.CASCADE, related_name='invitations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    status = models.CharField(max_length=15, default=InvitationStatus.Waiting, choices=InvitationStatus.choices)

    class Meta:
        unique_together = ('invitee', 'team')


class Event(models.Model):
    class EventType(models.TextChoices):
        Team = "Team"
        Individual = "Individual"

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
    accessible_after_closure = models.BooleanField(default=False)
    crispWebsiteId = models.CharField(max_length=50, blank=True, null=True)

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
            return self.registration_form.registration_receipts.filter(is_participating=True)
        return RegistrationReceipt.objects.none()

    def delete(self, using=None, keep_parents=False):
        self.registration_form.delete() if self.registration_form is not None else None
        self.merchandise.delete() if self.merchandise is not None else None
        return super(Event, self).delete(using, keep_parents)


class FSMManager(models.Manager):
    @transaction.atomic
    def create(self, **args):
        fsm = super().create(**args)
        fsm.mentors.add(fsm.creator)
        # ct = ContentType.objects.get_for_model(institute)
        # assign_perm(Permission.objects.filter(codename='add_admin', content_type=ct).first(), institute.owner, institute)
        # these permission settings worked correctly but were too messy
        fsm.save()
        return fsm


class FSM(models.Model):
    class FSMLearningType(models.TextChoices):
        Supervised = 'Supervised'
        Unsupervised = 'Unsupervised'

    class FSMPType(models.TextChoices):
        Team = 'Team'
        Individual = 'Individual'
        Hybrid = 'Hybrid'

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, related_name='fsms', default=None, null=True,
                              blank=True)
    merchandise = models.OneToOneField('accounts.Merchandise', related_name='fsm', on_delete=models.SET_NULL, null=True,
                                       blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='fsm', on_delete=models.SET_NULL, null=True,
                                             blank=True)
    creator = models.ForeignKey('accounts.User', related_name='created_fsms', on_delete=models.SET_NULL, null=True,
                                blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='fsms', on_delete=models.SET_NULL,
                               null=True, blank=True)
    mentors = models.ManyToManyField('accounts.User', related_name='fsms', blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='workshop/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_state = models.OneToOneField('fsm.State', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.Unsupervised,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(max_length=40, default=FSMPType.Individual, choices=FSMPType.choices)
    lock = models.CharField(max_length=10, null=True, blank=True)
    team_size = models.IntegerField(default=3)

    objects = FSMManager()

    # TODO - make locks as mixins

    def __str__(self):
        return self.name

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.holder.admins.all()) if self.holder is not None else set()
        modifiers |= set(self.mentors.all())
        return modifiers


class Player(models.Model):
    user = models.ForeignKey(User, related_name='players', on_delete=models.CASCADE)
    fsm = models.ForeignKey(FSM, related_name='players', on_delete=models.CASCADE)
    receipt = models.ForeignKey(RegistrationReceipt, related_name='players', on_delete=models.CASCADE)
    current_state = models.ForeignKey('fsm.State', null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='players')
    last_visit = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def team(self):
        return self.receipt.team if self.receipt else None

    class Meta:
        unique_together = ('user', 'fsm')

    def __str__(self):
        return f'{self.user.full_name} in {self.fsm.name}'


class State(Paper):
    name = models.TextField(null=True, blank=True)
    fsm = models.ForeignKey(FSM, on_delete=models.CASCADE, related_name='states')

    @transaction.atomic
    def delete(self):
        try:
            if self.my_fsm:
                fsm = self.fsm
                fsm.first_state = fsm.states.exclude(id=self.id).first()
                fsm.save()
        except:
            pass
        return super(State, self).delete()

    def __str__(self):
        return f'{self.name} in {str(self.fsm)}'


# class StateAnswerSheet(AnswerSheet):
#     answer_sheet_of = models.ForeignKey(State, related_name='answer_sheets', on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, related_name='answer_sheets', on_delete=models.CASCADE)
#

class Hint(Paper):
    reference = models.ForeignKey(State, on_delete=models.CASCADE, related_name='hints')


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=25)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Article(Paper):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='workshop/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles')
    is_draft = models.BooleanField(default=True)
    publisher = models.ForeignKey('accounts.EducationalInstitute', related_name='articles', on_delete=models.SET_NULL,
                                  null=True, blank=True)


class EdgeManager(models.Manager):
    @transaction.atomic
    def create(self, **args):
        lock = args.get('lock', None)
        has_lock = False
        if lock:
            has_lock = True
        return super(EdgeManager, self).create(**{'has_lock': has_lock, **args})

    def update(self, instance, **args):
        lock = args.get('lock', None)
        has_lock = False
        if lock or instance.lock:
            has_lock = True
        return super(EdgeManager, self).update(instance, **{'has_lock': has_lock, **args})


# from tail to head
class Edge(models.Model):
    tail = models.ForeignKey(State, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(State, on_delete=models.CASCADE, related_name='inward_edges')
    is_back_enabled = models.BooleanField(default=True)
    min_score = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    priority = models.IntegerField(null=True, blank=True)
    lock = models.CharField(max_length=10, null=True, blank=True)
    has_lock = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)
    text = models.TextField(null=True, blank=True)

    objects = EdgeManager()

    class Meta:
        unique_together = ('tail', 'head')

    def __str__(self):
        return f'از {self.tail.name} به {self.head.name}'


class PlayerHistory(models.Model):
    player = models.ForeignKey('fsm.Player', on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='player_histories')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    entered_by_edge = models.ForeignKey(Edge, related_name='histories', default=None, null=True, blank=True,
                                        on_delete=models.SET_NULL)
    reverse_enter = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.player.id}-{self.state.name}'


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

    # TODO - change paper on delete to cascade
    name = models.CharField(max_length=100, null=True, blank=True)
    paper = models.ForeignKey(Paper, null=True, blank=True, on_delete=models.SET_NULL, related_name='widgets')
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices, null=False, blank=False)
    creator = models.ForeignKey('accounts.User', related_name='widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)
    duplication_of = models.ForeignKey('Widget', default=None, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='duplications')

    class Meta:
        order_with_respect_to = 'paper'


class Description(Widget):
    text = models.TextField()
    is_spoilbox = models.BooleanField(default=False)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Game(Widget):
    link = models.TextField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Video(Widget):
    link = models.TextField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Image(Widget):
    link = models.TextField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Problem(Widget):
    text = models.TextField(null=True, blank=True)
    help_text = models.TextField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)
    required = models.BooleanField(default=False)
    max_corrections = models.IntegerField(null=True, blank=True)

    @property
    def solution(self):
        return self.answers.filter(is_solution=True).first()

    def unfinalize_older_answers(self, user):
        if isinstance(self.paper, State):
            teammates = Team.objects.get_teammates_from_widget(user=user, widget=self)
            older_answers = PROBLEM_ANSWER_MAPPING[self.widget_type].objects.filter(problem=self, is_final_answer=True,
                                                                                    submitted_by__in=teammates)
            for a in older_answers:
                a.is_final_answer = False
                a.save()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


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


class Answer(PolymorphicModel):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices, null=False, blank=False)
    answer_sheet = models.ForeignKey(AnswerSheet, related_name='answers', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    submitted_by = models.ForeignKey('accounts.User', related_name='submitted_answers',
                                     null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final_answer = models.BooleanField(default=False)
    is_solution = models.BooleanField(default=False)

    @property
    def problem(self):
        return self.problem


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
    problem = models.ForeignKey('fsm.BigAnswerProblem', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    text = models.TextField()


class ChoiceSelection(models.Model):
    multi_choice_answer = models.ForeignKey('MultiChoiceAnswer', on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='selections')


class MultiChoiceAnswer(Answer):
    problem = models.ForeignKey('fsm.MultiChoiceProblem', null=True, blank=True, on_delete=models.CASCADE,
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
    problem = models.ForeignKey('fsm.UploadFileProblem', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='answers')
    answer_file = models.FileField(upload_to='answers', max_length=4000, blank=False)


class Font(models.Model):
    font_file = models.FileField(upload_to='fonts/', blank=False)

    @property
    def name(self):
        return self.font_file.name if not self.font_file.name.startswith('fonts/') else self.font_file.name[6:]

    def __str__(self) -> str:
        return self.name


class CertificateTemplate(models.Model):
    certificate_type = models.CharField(max_length=50, null=True, blank=True)  # i.e. gold, silver, etc.
    template_file = models.FileField(upload_to='certificate_templates/', null=True, blank=True)
    name_X = models.IntegerField(null=True, blank=True, default=None)
    name_Y = models.IntegerField(null=True, blank=True, default=None)
    registration_form = models.ForeignKey(RegistrationForm, on_delete=models.CASCADE,
                                          related_name='certificate_templates')
    font = models.ForeignKey(Font, on_delete=models.SET_NULL, related_name='templates', null=True)
    font_size = models.IntegerField(default=100)


PROBLEM_ANSWER_MAPPING = {
    'SmallAnswerProblem': SmallAnswer,
    'BigAnswerProblem': BigAnswer,
    'MultiChoiceProblem': MultiChoiceAnswer,
    'UploadFileProblem': UploadFileAnswer,
}


# ---------
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
    current_state = models.ForeignKey(State, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='player_workshop')
    last_visit = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.id}:{str(self.player)}-{self.workshop.name}'
