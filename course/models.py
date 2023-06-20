from django.db import models

from my_form.models import RegistrationForm, RegistrationReceipt


class Course(models.Model):
    class CourseType(models.TextChoices):
        Team = "Team"
        Individual = "Individual"

    merchandise = models.OneToOneField('accounts.Merchandise', related_name='course', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    registration_form = models.OneToOneField(RegistrationForm, related_name='course', on_delete=models.SET_NULL,
                                             null=True, blank=True)
    creator = models.ForeignKey('accounts.User', related_name='courses', on_delete=models.SET_NULL, null=True,
                                blank=True)
    holder = models.ForeignKey('accounts.EducationalInstitute', related_name='courses', on_delete=models.SET_NULL,
                               null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(upload_to='courses/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(
        max_length=40, default=CourseType.Individual, choices=CourseType.choices)
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
        return super(Course, self).delete(using, keep_parents)
