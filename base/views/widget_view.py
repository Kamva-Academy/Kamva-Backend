from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error
from fsm.models import Team
from base.models import Widget
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from base.permissions import CanSubmitAnswer
from question_widget.models import PROBLEM_ANSWER_MAPPING
from question_widget.serializers.answer_polymorphic_serializer import AnswerPolymorphicSerializer, MockAnswerSerializer
from base.serializers.widget_serializers import MockWidgetSerializer
from base.serializers.widget_polymorphic import WidgetPolymorphicSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
@transaction.atomic
def upload_widget_file(request, widget_id):
    file = request.FILES.get('file', None)
    widget = Widget.objects.get(id=widget_id)
    widget.file = file
    widget.save()
    return Response(WidgetPolymorphicSerializer(widget).data, status.HTTP_200_OK)


class WidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes([MultiPartParser])
    queryset = Widget.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['widget']

    # todo - manage permissions

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['submit_answer', 'make_empty', 'answers']:
            permission_classes = [CanSubmitAnswer]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(tags=['widget'])
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, ])
    def make_widget_file_empty(self, request, *args, **kwargs):
        self.get_object().make_file_empty()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = WidgetPolymorphicSerializer(
            data=request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WidgetPolymorphicSerializer(
            instance, data=request.data, partial=True, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AnswerPolymorphicSerializer,
            permission_classes=[CanSubmitAnswer, ])
    def submit_answer(self, request, *args, **kwargs):
        data = {'is_final_answer': True, **request.data}
        if 'problem' not in data.keys():
            data['problem'] = self.get_object().id
        elif data.get('problem', None) != self.get_object().id:
            raise ParseError(serialize_error('4101'))
        serializer = AnswerPolymorphicSerializer(
            data=data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanSubmitAnswer, ])
    def make_empty(self, request, *args, **kwargs):
        self.get_object().unfinalize_older_answers(request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanSubmitAnswer, ])
    def answers(self, request, *args, **kwargs):
        teammates = Team.objects.get_teammates_from_widget(
            user=request.user, widget=self.get_object())
        older_answers = PROBLEM_ANSWER_MAPPING[self.get_object().widget_type].objects.filter(problem=self.get_object(),
                                                                                             submitted_by__in=teammates)
        return Response(data=AnswerPolymorphicSerializer(older_answers, many=True).data, status=status.HTTP_200_OK)
