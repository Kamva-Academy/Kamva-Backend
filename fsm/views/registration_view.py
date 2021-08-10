from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts import permissions
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer
from fsm.serializers.paper_serializers import PaperPolymorphicSerializer, RegistrationFormSerializer, \
    ChangeWidgetOrderSerializer
from fsm.models import RegistrationForm, transaction, AnswerSheet
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
        return Response(data=RegistrationFormSerializer(self.get_object()).data)

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
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
