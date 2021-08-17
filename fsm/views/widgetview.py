from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from fsm.models import *
from rest_framework import permissions
from fsm.serializers.widget_serializers import WidgetSerializer

import sys


class WidgetView(GenericViewSet, RetrieveModelMixin,):
    permission_classes = [permissions.AllowAny]
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer

