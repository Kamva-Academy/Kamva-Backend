from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from accounts.models import User
from errors.error_codes import serialize_error
from fsm.models import RegistrationReceipt, RegistrationForm
from fsm.permissions import IsRegistrationReceiptOwner, IsReceiptsFormModifier
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer, RegistrationInfoSerializer, \
    RegistrationStatusSerializer


class RegistrationReceiptViewSet(GenericViewSet, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = RegistrationReceiptSerializer
    queryset = RegistrationReceipt.objects.all()
    my_tags = ['registration']

    serializer_action_classes = {
        'validate_receipt': RegistrationStatusSerializer
    }

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsRegistrationReceiptOwner]
        elif self.action == 'retrieve':
            permission_classes = [IsRegistrationReceiptOwner | IsReceiptsFormModifier]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return RegistrationReceipt.objects.none()
        return self.queryset

    @swagger_auto_schema(responses={200: RegistrationReceiptSerializer})
    @action(detail=True, methods=['post'], serializer_class=RegistrationStatusSerializer)
    @transaction.atomic
    def validate(self, request, pk=None):
        receipt = self.get_object()
        if self.request.user not in receipt.answer_sheet_of.event_or_fsm.modifiers:
            raise PermissionDenied(serialize_error('4061'))
        if not self.request.user.school_studentship.is_document_verified:
            raise PermissionDenied(serialize_error('4062'))
        status_serializer = RegistrationStatusSerializer(data=self.request.data)
        if status_serializer.is_valid(raise_exception=True):
            registration_status = status_serializer.data.get('status', RegistrationReceipt.RegistrationStatus.Waiting)

            if registration_status == RegistrationReceipt.RegistrationStatus.Accepted:
                merchandise = receipt.answer_sheet_of.event_or_fsm.merchandise
                if receipt.answer_sheet_of is not None and (merchandise is None or merchandise.price == 0):
                    receipt.is_participating = True
            else:
                receipt.is_participating = False
            receipt.status = registration_status
            receipt.save()
            return Response(RegistrationReceiptSerializer().to_representation(receipt), status=status.HTTP_200_OK)
