from django.db import models
from polymorphic.models import PolymorphicModel
from accounts.models import User


class Paper(PolymorphicModel):
    class PaperType(models.TextChoices):
        RegistrationForm = 'RegistrationForm'
        State = 'State'
        Hint = 'Hint'
        WidgetHint = 'WidgetHint'
        Article = 'Article'

    paper_type = models.CharField(
        max_length=25, blank=False, choices=PaperType.choices)
    creator = models.ForeignKey('accounts.User', related_name='new_papers', null=True, blank=True,
                                on_delete=models.SET_NULL)
    since = models.DateTimeField(null=True, blank=True)
    till = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, default=None)
    is_exam = models.BooleanField(default=False)
    criteria = models.OneToOneField('scoring.Criteria', related_name='new_paper', null=True, blank=True,
                                    on_delete=models.CASCADE)

    def delete(self):
        for w in Widget.objects.filter(paper=self):
            try:
                w.delete()
            except:
                w.paper = None
                w.save()
        return super(Paper, self).delete()

    def is_user_permitted(self, user: User):
        if self.criteria:
            return self.criteria.evaluate(user)
        return True

    def __str__(self):
        return f"{self.paper_type}"


class Widget(PolymorphicModel):
    class WidgetTypes(models.TextChoices):
        Game = 'Game'
        Video = 'Video'
        Image = 'Image'
        Aparat = 'Aparat'
        Audio = 'Audio'
        Description = 'Description'
        SmallAnswerProblem = 'SmallAnswerProblem'
        BigAnswerProblem = 'BigAnswerProblem'
        MultiChoiceProblem = 'MultiChoiceProblem'
        UploadFileProblem = 'UploadFileProblem'
        Scorable = 'Scorable'

    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to='events/')
    paper = models.ForeignKey(
        Paper, null=True, blank=True, on_delete=models.CASCADE, related_name='new_widgets')
    widget_type = models.CharField(
        max_length=30, choices=WidgetTypes.choices, null=False, blank=False)
    creator = models.ForeignKey('accounts.User', related_name='new_widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)

    class Meta:
        order_with_respect_to = 'paper'

    def make_file_empty(self):
        try:
            self.file.delete()
        except:
            self.file = None
            self.file.save()
            pass
