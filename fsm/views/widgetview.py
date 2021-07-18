from rest_framework import viewsets
from rest_framework import mixins

from fsm.models import *
from rest_framework import permissions
from fsm.serializers.widget_serializers import WidgetSerializer

import sys


class WidgetView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    #permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]
    permission_classes = [permissions.AllowAny]
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer

    @transaction.atomic
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            try:
                return WidgetSerializer.get_serializer(getattr(sys.modules[__name__], self.request.data['widget_type']))
            except:
                pass
        
        # class WidgetInstanceSerializer(WidgetSerializer):
        #     class Meta:
        #         try:
        #             model =  getattr(sys.modules[__name__],
        #                 self.request.data['widget_type']
        #             ) if self.request.data['widget_type'] else Widget
        #         except:
        #             model = Widget
        #
        #         fields = '__all__'vah
        # return WidgetInstanceSerializer
