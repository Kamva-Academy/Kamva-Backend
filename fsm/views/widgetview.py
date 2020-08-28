from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import *
from rest_framework import permissions
from fsm.views import permissions as customPermissions
from fsm.serializers import WidgetSerializer

import sys

class WidgetView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    #permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]
    permission_classes = [permissions.AllowAny]
    queryset = Widget.objects.all().select_subclasses()
    serializer_class = WidgetSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            try:
                return WidgetSerializer.get_serializer(getattr(sys.modules[__name__],\
                    self.request.data['widget_type']))
            except:
                pass
        
        class WidgetInstanceSerializer(WidgetSerializer): 
            class Meta:
                try:
                    model =  getattr(sys.modules[__name__], 
                        self.request.data['widget_type']
                    ) if self.request.data['widget_type'] else Widget
                except:
                    model = Widget
                    
                fields = '__all__'

        return WidgetInstanceSerializer
    