from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from fsm.models import PlayerHistory
from fsm.views import permissions as customPermissions
from fsm.serializers import TeamHistorySerializer

class TeamHistoryView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]
    #permission_classes = [permissions.AllowAny]

    queryset = PlayerHistory.objects.all()
    serializer_class = TeamHistorySerializer
