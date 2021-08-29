from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from accounts.serializers import AccountSerializer
from accounts.utils import find_user
from errors.error_codes import serialize_error
from fsm.models import FSM, State
from fsm.permissions import MentorPermission, HasActiveRegistration
from fsm.serializers.fsm_serializers import FSMSerializer, FSMGetSerializer
from fsm.serializers.paper_serializers import StateSerializer


class FSMViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FSM.objects.all()
    serializer_class = FSMSerializer
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action == 'update' or self.action == 'destroy' or self.action == 'add_mentor' or self.action == 'get_states':
            permission_classes = [MentorPermission]
        elif self.action == 'enter':
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @swagger_auto_schema(responses={200: StateSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def enter(self, request, pk=None):
        fsm = self.get_object()
        user = self.request.user
        # TODO - complete it or DIE


    @swagger_auto_schema(responses={200: StateSerializer})
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def get_states(self):
        return Response(data=StateSerializer(self.get_object().states, many=True).data, status=status.HTTP_200_OK)


    @swagger_auto_schema(responses={200: FSMSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AccountSerializer, permission_classes=[MentorPermission, ])
    def add_mentor(self, request, pk=None):
        data = request.data
        fsm = self.get_object()
        serializer = AccountSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_mentor = find_user(serializer.validated_data)
            fsm.mentors.add(new_mentor)
            return Response(FSMSerializer(fsm).data, status=status.HTTP_200_OK)
