from django.db import transaction
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from fsm.models import Answer, UploadFileAnswer
from fsm.permissions import IsAnswerModifier
from fsm.serializers.answer_serializers import AnswerSerializer, UploadFileAnswerSerializer, AnswerPolymorphicSerializer


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


class AnswerViewSet(ModelViewSet):
    serializer_class = AnswerPolymorphicSerializer
    queryset = Answer.objects.all()
    my_tags = ['answers']
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super(AnswerViewSet, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['destroy', 'update']:
            permission_classes = [IsAnswerModifier]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]