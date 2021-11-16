from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import viewsets
from rest_framework.response import Response

from fsm.models import *
from rest_framework import permissions

from fsm.permissions import CanAnswerWidget
from fsm.serializers.answer_serializers import AnswerPolymorphicSerializer, MockAnswerSerializer
from fsm.serializers.widget_serializers import WidgetPolymorphicSerializer, MockWidgetSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Widget.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['widgets']

    # todo - manage permissions

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['submit_answer']:
            permission_classes = [CanAnswerWidget]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        context.update({'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = WidgetPolymorphicSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AnswerPolymorphicSerializer,
            permission_classes=[CanAnswerWidget, ])
    def submit_answer(self, request, *args, **kwargs):
        data = {'is_final_answer': True, **request.data}
        if 'problem' not in data.keys():
            data['problem'] = self.get_object().id
        elif data['problem'] != self.get_object().id:
            raise ParseError(serialize_error('4101'))
        serializer = AnswerPolymorphicSerializer(data=data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            teammates = Team.objects.get_teammates_from_widget(user=request.user, widget=self.get_object())
            older_answers = PROBLEM_ANSWER_MAPPING[self.get_object().widget_type].objects.filter(
                problem=self.get_object(), is_final_answer=True, submitted_by__in=teammates)
            for a in older_answers:
                a.is_final_answer = False
                a.save()
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
