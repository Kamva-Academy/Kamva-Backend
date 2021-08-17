from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts import permissions
from errors.error_codes import serialize_error
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer
from fsm.serializers.paper_serializers import PaperPolymorphicSerializer, RegistrationFormSerializer, \
    ChangeWidgetOrderSerializer
from fsm.models import RegistrationForm, transaction, AnswerSheet, RegistrationReceipt
from fsm.views.permissions import IsRegistrationFormModifier


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationFormSerializer
    queryset = RegistrationForm.objects.all()
    my_tags = ['registration']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        return context

    def get_permissions(self):
        if self.action == 'create' or self.action == 'register' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsRegistrationFormModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: RegistrationFormSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=ChangeWidgetOrderSerializer)
    def change_order(self, request, pk=None):
        serializer = ChangeWidgetOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.get_object().set_widget_order(serializer.validated_data.get('order'))
        return Response(data=RegistrationFormSerializer(self.get_object()).data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(responses={201: RegistrationReceiptSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=RegistrationReceiptSerializer)
    def register(self, request, pk=None):
        context = self.get_serializer_context()
        context['answer_sheet_of'] = self.get_object()
        serializer = RegistrationReceiptSerializer(data={'answer_sheet_type': 'RegistrationReceipt',
                                                         **request.data}, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['answer_sheet_of'] = self.get_object()
            registration_receipt = serializer.save()
            if registration_receipt.does_pass_conditions():
                form = registration_receipt.answer_sheet_of
                event = form.event
                # TODO - handle fsm sign up
                if event:
                    if event.maximum_participant is None or len(event.participants) < event.maximum_participant:
                        if form.accepting_status == RegistrationForm.AcceptingStatus.AutoAccept:
                            registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
                            if not event.merchandise:
                                registration_receipt.is_participating = True
                            registration_receipt.save()
                        elif form.accepting_status == RegistrationForm.AcceptingStatus.CorrectAccept:
                            if registration_receipt.correction_status() == RegistrationReceipt.CorrectionStatus.Correct:
                                registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
                                if not event.merchandise:
                                    registration_receipt.is_participating = True
                                registration_receipt.save()
                    else:
                        registration_receipt.status = RegistrationReceipt.RegistrationStatus.Rejected
                        registration_receipt.save()
                        raise ParseError(serialize_error('4035'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
