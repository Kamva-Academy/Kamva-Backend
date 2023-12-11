from django.core.management.base import BaseCommand
from apps.fsm.models import TextWidget, Widget


class Command(BaseCommand):

    def handle(self, *args, **options):
        for text in TextWidget.objects.all():
            text.widget_type = Widget.WidgetTypes.TextWidget
            text.save()
