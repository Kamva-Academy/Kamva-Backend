import datetime
from django.db import models
from apps.accounts.models import Purchase

from apps.base.models import Paper
from apps.question_widget.models import MultiChoiceAnswer, ShortAnswer
from apps.scoring.models import Deliverable
from django.core.validators import MaxValueValidator, MinValueValidator


class Form(Paper):
    class AcceptingStatus(models.TextChoices):
        AutoAccept = 'AutoAccept'
        CorrectAccept = 'CorrectAccept'
        Manual = 'Manual'

    class GenderPartitionStatus(models.TextChoices):
        OnlyMale = 'OnlyMale'
        OnlyFemale = 'OnlyFemale'
        BothPartitioned = 'BothPartitioned'
        BothNonPartitioned = 'BothNonPartitioned'

    class SubmissionPermissionStatus(models.TextChoices):
        DeadlineMissed = "DeadlineMissed"
        NotStarted = "NotStarted"
        StudentshipDataIncomplete = "StudentshipDataIncomplete"
        NotPermitted = "NotPermitted"
        GradeNotAvailable = "GradeNotAvailable"
        StudentshipDataNotApproved = "StudentshipDataNotApproved"
        Permitted = "Permitted"
        NotRightGender = "NotRightGender"

    class AudienceType(models.TextChoices):
        Student = 'Student'
        Academic = 'Academic'
        All = 'All'

    min_grade = models.IntegerField(
        default=0, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = models.IntegerField(
        default=12, validators=[MaxValueValidator(12), MinValueValidator(0)])

    # TODO - add filter for audience type

    conditions = models.TextField(null=True, blank=True)

    accepting_status = models.CharField(
        max_length=15, default='AutoAccept', choices=AcceptingStatus.choices)
    gender_partition_status = models.CharField(max_length=25, default='BothPartitioned',
                                               choices=GenderPartitionStatus.choices)
    audience_type = models.CharField(
        max_length=50, default='Student', choices=AudienceType.choices)

    def get_user_permission_status(self, user):
        time_check_result = self.check_time()
        if time_check_result != 'ok':
            return time_check_result

        # if exec(self.answer_sheet_of.conditions):
        #     return True
        # TODO - handle for academic studentship too

        gender_check_result = self.check_gender(user)
        if gender_check_result != 'ok':
            return gender_check_result

        if self.audience_type == self.AudienceType.Academic:
            studentship = user.academic_studentship
            if studentship:
                if not studentship.university:
                    return self.SubmissionPermissionStatus.StudentshipDataIncomplete
            else:
                return self.SubmissionPermissionStatus.StudentshipDataNotApproved
        elif self.audience_type == self.AudienceType.Student:
            studentship = user.school_studentship
            if studentship:
                if studentship.grade:
                    if self.min_grade <= studentship.grade <= self.max_grade:
                        if studentship.school is not None or studentship.document is not None:

                            return self.SubmissionPermissionStatus.Permitted
                        else:
                            return self.SubmissionPermissionStatus.StudentshipDataIncomplete
                    else:
                        return self.SubmissionPermissionStatus.NotPermitted
                else:
                    return self.SubmissionPermissionStatus.GradeNotAvailable
            else:
                return self.SubmissionPermissionStatus.StudentshipDataNotApproved
        return self.SubmissionPermissionStatus.Permitted

    def check_time(self):
        if self.till and datetime.now(self.till.tzinfo) > self.till:
            return self.SubmissionPermissionStatus.DeadlineMissed
        if self.since and datetime.now(self.since.tzinfo) < self.since:
            return self.SubmissionPermissionStatus.NotStarted
        return 'ok'

    def check_gender(self, user):
        if (self.gender_partition_status == 'OnlyFemale' and user.gender == 'Male') or \
                (self.gender_partition_status == 'OnlyMale' and user.gender == 'Female'):
            return self.SubmissionPermissionStatus.NotRightGender
        return 'ok'

    def __str__(self):
        return f'<{self.id}-{self.paper_type}>'


class Receipt(Deliverable):
    class ReceiptType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"

    user = models.ForeignKey('accounts.User', related_name='new_registration_receipts', on_delete=models.CASCADE,
                             null=True, blank=True)
    form = models.ForeignKey(
        Form, null=True, on_delete=models.SET_NULL, related_name='receipts')
    type = models.CharField(max_length=25, blank=False,
                            choices=ReceiptType.choices)

    # should be in every answer sheet child
    form = models.ForeignKey(Form, related_name='receipts', null=True, blank=True,
                             on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('user', 'form')

    def delete(self):
        self.answers.clear()
        return super(Deliverable, self).delete()


class RegistrationReceipt(Receipt):
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

    status = models.CharField(max_length=25, blank=False,
                              default='Waiting', choices=RegistrationStatus.choices)
    is_participating = models.BooleanField(default=False)
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL,
                              related_name='new_members', null=True, blank=True)
    certificate = models.FileField(
        upload_to='certificates/', null=True, blank=True, default=None)

    @property
    def purchases(self):
        if self.answer_sheet_of.event_or_fsm.merchandise:
            return self.answer_sheet_of.event_or_fsm.merchandise.purchases.filter(user=self.user)
        return Purchase.objects.none()

    @property
    def is_paid(self):
        return len(self.purchases.filter(
            status=Purchase.Status.Success)) > 0 if self.answer_sheet_of.event_or_fsm.merchandise else True

    def correction_status(self):
        for a in self.answers.all():
            if isinstance(a, (ShortAnswer, MultiChoiceAnswer)):
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


class RegistrationForm(Form):
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

    def __str__(self):
        return f'<{self.id}-{self.paper_type}>:{self.event_or_fsm.name if self.event_or_fsm else None}'
