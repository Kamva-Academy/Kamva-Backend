from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import FSMEdge
from fsm.views import permissions
from fsm.serializers import FSMEdgeSerializer


class FSMEdgeView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = []
    queryset = FSMEdge.objects.all()
    serializer_class = FSMEdgeSerializer
