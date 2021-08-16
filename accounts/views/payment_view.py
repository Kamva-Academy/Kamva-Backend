import logging

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from accounts import zarinpal
from accounts.models import Merchandise, Purchase, DiscountCode, User
from accounts.permissions import IsPurchaseOwner
from accounts.serializers import DiscountCodeSerializer, PurchaseSerializer
from accounts.views.views import logger
from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from fsm.models import RegistrationReceipt

logger = logging.getLogger(__name__)


class PaymentViewSet(GenericViewSet, RetrieveModelMixin):
    my_tags = ['payments']
    serializer_class = DiscountCodeSerializer
    serializer_action_classes = {
        'verify_discount': DiscountCodeSerializer,
        'purchase': DiscountCodeSerializer,
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'verify_discount' or self.action == 'purchase':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'verify_payment':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsPurchaseOwner]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_queryset(self):
        if self.action == 'verify_discount' or self.action == 'purchase' or self.action == 'retrieve':
            return Merchandise.objects.all()
        else:
            return Purchase.objects.all()

    @transaction.atomic
    @action(detail=False, methods=['post'], serializer_class=DiscountCodeSerializer)
    def verify_discount(self, request, pk=None):
        serializer = DiscountCodeSerializer(data=request.data, context=self.get_serializer_context())

        if serializer.is_valid(raise_exception=True):
            code = serializer.data.get('code', None)
            merch_id = serializer.data.get('merchandise', None)
            discount_code = get_object_or_404(DiscountCode, code=code)
            merchandise = get_object_or_404(Merchandise, id=merch_id)
            new_price = DiscountCode.calculate_discount(discount_code.value, merchandise.price)
            return Response({'new_price': new_price, **serializer.to_representation(discount_code)},
                            status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: PurchaseSerializer})
    @transaction.atomic
    @action(detail=False, methods=['post'], serializer_class=DiscountCodeSerializer)
    def purchase(self, request, pk=None):
        serializer = DiscountCodeSerializer(data=request.data, context=self.get_serializer_context())

        if serializer.is_valid(raise_exception=True):
            code = serializer.data.get('code', None)
            merch_id = serializer.data.get('merchandise', None)
            discount_code = get_object_or_404(DiscountCode, code=code) if code else None
            merchandise = get_object_or_404(Merchandise, id=merch_id)
            registration_form = merchandise.event_or_fsm.registration_form
            if not registration_form:
                raise InternalServerError(serialize_error('5004'))
            user_registration = registration_form.registration_receipts.filter(user=request.user).last()
            if user_registration:
                if user_registration.status == RegistrationReceipt.RegistrationStatus.Accepted:
                    if len(merchandise.purchases.filter(user=self.request.user, status=Purchase.Status.Success)) > 0:
                        raise ParseError(serialize_error('4046'))
                    if discount_code:
                        price = DiscountCode.calculate_discount(discount_code.value, merchandise.price)
                        discount_code.is_valid = False
                        discount_code.save()
                    else:
                        price = merchandise.price
                    purchase = Purchase.objects.create_purchase(merchandise=merchandise, user=self.request.user,
                                                                amount=price, discount_code=discount_code)
                    callback_url = f'{self.reverse_action(self.verify_payment.url_name)}?id={request.user.id}&uniq_code={purchase.uniq_code}'
                    response = zarinpal.send_request(amount=price, description=merchandise.name,
                                                     callback_url=callback_url)

                    return Response({'payment_link': response, **PurchaseSerializer().to_representation(purchase)},
                                    status=status.HTTP_200_OK)
                else:
                    raise ParseError(serialize_error('4045'))
            else:
                raise ParseError(serialize_error('4044'))

    @transaction.atomic
    @action(detail=False, methods=['get'])
    def verify_payment(self, request):
        user = get_object_or_404(User, id=request.GET.get('id', None))
        purchase = get_object_or_404(Purchase, uniq_code=request.GET.get('uniq_code'), status=Purchase.Status.Started)
        logger.warning(f'Zarinpal callback: {request.GET}')
        res = zarinpal.verify(status=request.GET.get('Status', None),
                              authority=request.GET.get('Authority', None),
                              amount=purchase.amount)
        if 200 <= int(res["status"]) <= 299:
            purchase.ref_id = str(res['ref_id'])
            purchase.authority = request.GET.get('Authority', None)
            if res['status'] == 200:
                purchase.status = Purchase.Status.Success
                receipt = purchase.registration_receipt
                receipt.is_participating = True
                receipt.save()
            else:
                purchase.status = Purchase.Status.Repetitious
            purchase.save()

            return redirect(f'{settings.PAYMENT["FRONT_HOST_SUCCESS"]}{purchase.uniq_code}')
        else:
            purchase.authority = request.GET.get('Authority')
            purchase.status = Purchase.Status.Failed
            purchase.save()
            return redirect(f'{settings.PAYMENT["FRONT_HOST_FAILURE"]}{purchase.uniq_code}')