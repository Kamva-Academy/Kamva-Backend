from django.db import transaction
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from fsm.serializers import RegistrationFormSerializer
from fsm.models import RegistrationForm


class RegistrationFormViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = RegistrationFormSerializer
    queryset = RegistrationForm.objects.all()
    my_tags = ['registration']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        return context
