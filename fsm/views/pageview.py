from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import FSMPage, Widget
from fsm.views import permissions
from fsm.serializers import FSMPageSerializer, WidgetSerializer


class FSMPageView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = []
    queryset = FSMPage.objects.all()
    serializer_class = FSMPageSerializer
    
    def create(self, request, *args, **kwargs):
        widgets_data = request.data['widgets']
        serializer = FSMPageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        instance = serializer.create(data)
        for widget_data in widgets_data:
            widgetSerializer = WidgetSerializer()
            widget = widgetSerializer.create(widget_data)
            widget.page = instance
            widget.save()
        
        response = serializer.to_representation(instance)
        return Response(response) 

    def update(self, request, *args, **kwargs):  
        instance = FSMPage.objects.filter(id=request.parser_context['kwargs'].get('pk', -1))[0]
        widgets = instance.widgets()
        for widget in widgets:
            widget.delete()
        index = 0
        while True:
            try:
                request.data['widgets'][index]['pk'] = request.data['widgets'][index]['id']
            except:
                break
            index+=1
        request.data['pk'] = instance.pk
        print(request.data)
        instance.delete()
        return self.create(request, *args, **kwargs)

