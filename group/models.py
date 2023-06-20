import uuid
from django.db import models

from my_form.models import RegistrationForm, RegistrationReceipt


class TeamManager(models.Manager):
    def get_group_from_widget(self, user, widget):
        form = widget.paper.fsm.registration_form or widget.paper.fsm.event.registration_form
        return Group.objects.filter(registration_form=form, members__user=user).first()

    def get_groupmates_from_widget(self, user, widget):
        group = self.get_group_from_widget(user, widget)
        return group.members.values_list('user', flat=True) if group is not None else [user]


class Group(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    registration_form = models.ForeignKey(RegistrationForm, related_name='groups', null=True, blank=True,
                                          on_delete=models.SET_NULL)
    head = models.OneToOneField(RegistrationReceipt, related_name='headed_group', null=True, blank=True,
                                on_delete=models.SET_NULL)

    chat_room = models.CharField(max_length=200, null=True, blank=True)

    objects = TeamManager()

    def __str__(self):
        return f'{self.name}:{",".join(member.user.full_name for member in self.members.all())}'


class Invitation(models.Model):
    class InvitationStatus(models.TextChoices):
        Waiting = "Waiting"
        Rejected = "Rejected"
        Accepted = "Accepted"

    invitee = models.ForeignKey(
        RegistrationReceipt, on_delete=models.CASCADE, related_name='invitations')
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='group_members')
    status = models.CharField(
        max_length=15, default=InvitationStatus.Waiting, choices=InvitationStatus.choices)

    # class Meta:
    #     unique_together = ('invitee', 'group')
