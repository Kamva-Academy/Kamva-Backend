from django.db import transaction
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from fsm.models import Answer, UploadFileAnswer
from fsm.serializers.answer_serializers import AnswerSerializer, UploadFileAnswerSerializer


class UploadAnswerViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin):
    serializer_class = UploadFileAnswerSerializer
    parser_classes = [MultiPartParser]
    queryset = UploadFileAnswer.objects.all()
    my_tags = ['answers']
    permission_classes = [IsAuthenticated,]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context
