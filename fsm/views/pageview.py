from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import FSMPage
from fsm.views import permissions
from fsm.serializers import FSMPageSerializer


class FSMPageView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = []
    queryset = FSMPage.objects.all()
    serializer_class = FSMPageSerializer

    def get_serializer_class(self):
        print("salam")
        return FSMPageSerializer