from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fsm.models import Event
from apps.fsm.serializers.fsm_serializers import EventSerializer
from apps.fsm.permissions import IsEventModifier, HasActiveRegistration


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    my_tags = ['event']
    filterset_fields = ['party', 'is_private']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'get_fsms':
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = [IsEventModifier]
        return [permission() for permission in permission_classes]
