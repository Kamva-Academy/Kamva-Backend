from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fsm.models import Event
from apps.fsm.serializers.fsm_serializers import EventSerializer, FSMSerializer
from apps.fsm.permissions import IsEventModifier, HasActiveRegistration


import logging

logger = logging.getLogger(__name__)


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    my_tags = ['event']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['create', 'get_mentored_fsms']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'get_fsms':
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = [IsEventModifier]
        return [permission() for permission in permission_classes]

    def list(self, request):
        return Response(data=self.serializer_class(Event.objects.filter(is_private=False), context={'request': request}, many=True).data, status=status.HTTP_200_OK)

    @transaction.atomic
    @swagger_auto_schema(responses={200: FSMSerializer}, tags=['mentor'])
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_mentored_fsms(self, request, pk=None):
        event_fsms = self.get_object().fsms.all()
        user = self.request.user
        fs = []
        for f in event_fsms:
            if user in f.mentors.all():
                fs.append(f)
        return Response(data=FSMSerializer(fs, many=True, context=self.get_serializer_context()).data,
                        status=status.HTTP_200_OK)
