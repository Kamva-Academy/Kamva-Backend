import logging

from django.conf import settings
from rest_framework.response import Response
from zeep import Client

logger = logging.getLogger(__name__)


ZARINPAL_CONFIG = settings.ZARINPAL_CONFIG


def send_request(amount, call_back_url, email=None, mobile=None):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    result = client.service.PaymentRequest(
        ZARINPAL_CONFIG['MERCHANT'],
        amount,
        ZARINPAL_CONFIG['DESCRIPTION'],
        email,
        mobile,
        call_back_url)
    if result.Status == 100:
        return Response({
            'redirect': f'https://www.zarinpal.com/pg/StartPay/{str(result.Authority)}'
        })
    else:
        logger.error(f'Zarinpal send request error: {result}')
        return Response({
            'msg': f'Error code: {str(result.Status)}'
        }, status=500)


def verify(status, authority, amount):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    if status == 'OK':
        result = client.service.PaymentVerification(ZARINPAL_CONFIG['MERCHANT'], authority, amount)
        if result.Status == 100:
            logger.info(f'Transaction success: {result}')
            return Response({
                'msg': 'Transaction success.',
                'ref_id': str(result.RefID)
            })
        elif result.Status == 101:
            logger.info(f'Transaction submitted: {result}')
            return Response({
                'msg': 'Transaction submitted.',
                'status': str(result.Status)
            })
        else:
            logger.error(f'Zarinpal verification error: {result}')
            return Response({
                'msg': 'Transaction failed!',
                'status': str(result.Status)
            }, status=400)
    else:
        logger.error(f'Zarinpal status not OK: {status}')
        return Response({
            'msg': 'Transaction failed or canceled by user'
        }, status=400)
