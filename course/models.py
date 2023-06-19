from django.db import models

from my_form.models import RegistrationForm, RegistrationReceipt


class Event(models.Model):
    class EventType(models.TextChoices):
        Team = "Team"
        Individual = "Individual"

    merchandise = models.OneToOneField('accounts.Merchandise', related_name='new_event', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='event', on_delete=models.SET_NULL,
                                             null=True, blank=True)
    creator = models.ForeignKey('accounts.User', related_name='new_events', on_delete=models.SET_NULL, null=True,
                                blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='new_events', on_delete=models.SET_NULL,
                               null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='events/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(
        max_length=40, default=EventType.Individual, choices=EventType.choices)
    team_size = models.IntegerField(default=3)
    maximum_participant = models.IntegerField(null=True, blank=True)
    accessible_after_closure = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.holder.admins.all()
                         ) if self.holder is not None else set()
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
