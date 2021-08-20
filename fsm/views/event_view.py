from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from fsm.models import Event
from fsm.serializers.fsm_serializers import EventSerializer
from fsm.permissions import IsEventModifier


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    my_tags = ['event']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsEventModifier]
        return [permission() for permission in permission_classes]

    # TODO - add list retrieve of all registration receipts
