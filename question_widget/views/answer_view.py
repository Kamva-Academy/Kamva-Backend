from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from question_widget.filtersets import AnswerFilterSet
from question_widget.models import Answer, UploadFileAnswer
from question_widget.permissions import IsAnswerModifier, MentorCorrectionPermission
from question_widget.serializers.answer_serializers import UploadFileAnswerSerializer
from question_widget.serializers.answer_polymorphic import AnswerPolymorphicSerializer


class UploadAnswerViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin):
    serializer_class = UploadFileAnswerSerializer
    parser_classes = [MultiPartParser]
    queryset = UploadFileAnswer.objects.all()
    my_tags = ['answers']
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context


class AnswerViewSet(GenericViewSet, UpdateModelMixin, RetrieveModelMixin, ListModelMixin):
    serializer_class = AnswerPolymorphicSerializer
    my_tags = ['answers']
    queryset = Answer.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnswerFilterSet
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super(AnswerViewSet, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsAnswerModifier]
        else:
            permission_classes = [MentorCorrectionPermission]
        return [permission() for permission in permission_classes]
