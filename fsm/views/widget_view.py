from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import viewsets

from fsm.models import *
from rest_framework import permissions
from fsm.serializers.widget_serializers import WidgetPolymorphicSerializer, MockWidgetSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Widget.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['widget']

    # todo - manage permissions

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        context.update({'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(WidgetViewSet, self).create(request, *args, **kwargs)
