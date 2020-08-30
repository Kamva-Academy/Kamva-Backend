from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import FSMState
from fsm.serializers import FSMStateSerializer, FSMStateGetSerializer

from rest_framework import permissions
from fsm.views import permissions as customPermissions


class FSMStateView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]

    queryset = FSMState.objects.all()
    serializer_class = FSMStateSerializer

    def get_serializer_class(self):
        return FSMStateGetSerializer \
            if self.request.method == 'GET' \
            else FSMStateSerializer
