from django.contrib.auth.models import AnonymousUser
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from fsm.models import RegistrationReceipt
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer


class RegistrationReceiptViewSet(GenericViewSet, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = RegistrationReceiptSerializer
    queryset = RegistrationReceipt.objects.all()
    my_tags = ['registration']

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return RegistrationReceipt.objects.none()
        elif user.is_staff or user.is_superuser:
            return RegistrationReceipt.objects.all()
        else:
            return RegistrationReceipt.objects.filter(user=user.id)

