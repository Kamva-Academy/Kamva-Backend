from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import FSMPage, Widget, FSMState
from rest_framework import permissions
from fsm.views import permissions as customPermissions
from fsm.serializers import FSMPageSerializer, WidgetSerializer, FSMStateSerializer


class FSMPageView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]
    queryset = FSMPage.objects.all()
    serializer_class = FSMPageSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        widgets_data = request.data['widgets']
        serializer = FSMPageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        for widget_data in widgets_data:
            widgetSerializer = WidgetSerializer()
            widget = widgetSerializer.create(widget_data)
            widget.page = instance
            widget.save()
        
        fsmStateSerializer = FSMStateSerializer(data=request.data['state'])
        if not fsmStateSerializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = fsmStateSerializer.validated_data
        try:
            data['pk'] = request.data['state']['pk']
        except:
            pass
        state = fsmStateSerializer.create(data)
        state.page = instance
        state.save()
        
        response = serializer.to_representation(instance)
        return Response(response)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        serializer = FSMPageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        instance = FSMPage.objects.filter(id=request.parser_context['kwargs'].get('pk', -1))[0]
        widgets = instance.widgets()
        request.data['state']['pk'] = instance.state.pk
        instance.state.delete()
        for widget in widgets:
            widget.delete()
        index = 0
        while True:
            try:
                widget_id = request.data['widgets'][index]['id']
                # check is not exist
                request.data['widgets'][index]['pk'] = widget_id
            except:
                break
            index+=1
        request.data['pk'] = instance.pk
        instance.delete()
        return self.create(request, *args, **kwargs)

