from django.db import models
from polymorphic.models import PolymorphicModel


class Creatable:
    creator = models.ForeignKey(
        'accounts.User', null=True, related_name='new_papers', on_delete=models.SET_NULL)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField()


class Paper(PolymorphicModel, Creatable):
    class PaperType(models.TextChoices):
        Form = 'Form'
        FSMState = 'FSMState'
        Hint = 'Hint'
        Article = 'Article'

    paper_type = models.CharField(max_length=25, choices=PaperType.choices)
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

    def __str__(self):
        return f"{self.paper_type}"


class Widget(PolymorphicModel, Creatable):
    class WidgetTypes(models.TextChoices):
        Question = 'Question'
        Content = 'Content'

    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    name = models.CharField(max_length=100, null=True, blank=True)
    paper = models.ForeignKey(
        Paper, on_delete=models.CASCADE, related_name='widgets', null=True, blank=True)

    class Meta:
        order_with_respect_to = 'paper'
