from django.db import models, transaction
from accounts.models import User
from base.models import Paper

from course.models import Event
from my_form.models import RegistrationForm, RegistrationReceipt


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
    merchandise = models.OneToOneField('accounts.Merchandise', related_name='new_fsm', on_delete=models.SET_NULL, null=True,
                                       blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='fsm', on_delete=models.SET_NULL, null=True,
                                             blank=True)
    creator = models.ForeignKey('accounts.User', related_name='new_created_fsms', on_delete=models.SET_NULL, null=True,
                                blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='new_fsms', on_delete=models.SET_NULL,
                               null=True, blank=True)
    mentors = models.ManyToManyField(
        'accounts.User', related_name='new_fsms', blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(
        upload_to='workshop/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_state = models.OneToOneField('finite_state_machine.State', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.Unsupervised,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(
        max_length=40, default=FSMPType.Individual, choices=FSMPType.choices)
    lock = models.CharField(max_length=10, null=True, blank=True)
    team_size = models.IntegerField(default=3)

    objects = FSMManager()

    # TODO - make locks as mixins

    def __str__(self):
        return self.name

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.holder.admins.all()
                         ) if self.holder is not None else set()
        modifiers |= set(self.mentors.all())
        return modifiers


class Player(models.Model):
    user = models.ForeignKey(
        User, related_name='new_players', on_delete=models.CASCADE)
    fsm = models.ForeignKey(FSM, related_name='players',
                            on_delete=models.CASCADE)
    receipt = models.ForeignKey(
        RegistrationReceipt, related_name='players', on_delete=models.CASCADE)
    current_state = models.ForeignKey('finite_state_machine.State', null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='players')
    last_visit = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def team(self):
        return self.receipt.team if self.receipt else None

    class Meta:
        unique_together = ('user', 'fsm', 'receipt')

    def __str__(self):
        return f'{self.user.full_name} in {self.fsm.name}'


class State(Paper):
    name = models.TextField(null=True, blank=True)
    fsm = models.ForeignKey(
        FSM, on_delete=models.CASCADE, related_name='states')

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
    tail = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='inward_edges')
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
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='histories')
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='player_histories')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    entered_by_edge = models.ForeignKey(Edge, related_name='histories', default=None, null=True, blank=True,
                                        on_delete=models.SET_NULL)
    reverse_enter = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.player.id}-{self.state.name}'
