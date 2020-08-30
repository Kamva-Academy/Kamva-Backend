from django.db import transaction
from django.shortcuts import get_object_or_404
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
    #permission_classes = [permissions.AllowAny]
    queryset = FSMPage.objects.all()
    serializer_class = FSMPageSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        widgets_data = request.data['widgets']
        data = request.data
        data['widgets'] = []
        serializer = FSMPageSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        instance.save()
        for widget_data in widgets_data:
            widget = Widget.objects.get(id = widget_data)
            widget.page = instance
            widget.save()
            # get widget by id
            # widgetSerializer = WidgetSerializer()
            # # widget = widgetSerializer.create(widget_data)
            # widget.page = instance
            # widget.save()


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
        page = get_object_or_404(FSMPage, id=request.parser_context['kwargs'].get('pk', -1))

        if 'page_type' in request.data:
            page.page_type = request.data['page_type']
        if 'stateId' in request.data:
            state = get_object_or_404(FSMState, id= request.data['pageId'])
            state.page = page
            state.save()

        old_widgets = page.widgets()
        new_widgets = request.data['widgets']
        if 'widgets' in request.data:
            for widgetId in new_widgets:
                widget = get_object_or_404(Widget, id=widgetId)
                widget.page = page
                widget.save()

        for widget in old_widgets:
            if widget.id not in new_widgets:
                widget.delete()

        page.save()
        response = serializer.to_representation(page)
        return Response(response)


