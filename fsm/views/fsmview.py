from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view
from rest_framework import permissions

from fsm.models import FSM
from fsm.views import permissions as customPermissions
from fsm.serializers import FSMSerializer, FSMGetSerializer

class FSMView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission]
    permission_classes_by_action = {
        'list': [permissions.IsAuthenticated],
        'retrieve': [permissions.IsAuthenticated]
    }
    #  permission_classes = [permissions.AllowAny]

    queryset = FSM.objects.all()
    serializer_class = FSMSerializer

    @transaction.atomic
    def get_serializer_class(self):
        return FSMGetSerializer \
            if self.request.method == 'GET' and self.request.user.is_mentor \
            else FSMSerializer

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
