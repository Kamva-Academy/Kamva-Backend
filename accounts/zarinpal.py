import logging

from django.conf import settings
from rest_framework.response import Response
from zeep import Client

logger = logging.getLogger(__name__)


ZARINPAL_CONFIG = settings.ZARINPAL_CONFIG


def send_request(amount, call_back_url, email=None, mobile=None):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    result = client.service.PaymentRequest(
        ZARINPAL_CONFIG['MERCHANT'],
        amount,
        ZARINPAL_CONFIG['DESCRIPTION'],
        email,
        mobile,
        call_back_url)
    if result.Status == 100:
        return {
            "message": f'{ZARINPAL_CONFIG["ROUTE_START_PAY"]}{str(result.Authority)}',
            'status': 201
        }
    else:
        logger.error(f'Zarinpal send request error: {result}')
        return {
            'message': f'برای درگاهی اینترنتی مشکلی پیش امده است لطفا با پشتیبانی رستا در تماس باشید:{str(result.Status)}',
            'status': 403
        }


def verify(status, authority, amount):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    if status == 'OK':
        result = client.service.PaymentVerification(ZARINPAL_CONFIG['MERCHANT'], authority, amount)
        if result.Status == 100:
            logger.info(f'Transaction success: {result}')
            return {
                'message': 'پرداخت با موفقیت انجام شد.',
                'ref_id': str(result.RefID),
                'status': 200
            }
        elif result.Status == 101:
            logger.warning(f'Transaction submitted: {result}')
            return {
                'message': 'این تراکنش قبلا بررسی شده است.',
                'ref_id': str(result.RefID),
                'status': 201
            }
        else:
            logger.warning(f'Zarinpal verification error: {result}')
            return {
                'message': 'تراکنش ناموفق بود',
                'status': 400
            }
    else:
        logger.warning(f'Transaction failed or canceled by authority: {authority}')
        return {
            'message': 'تراکنش ناموفق بوده است یا توسط کاربر کنسل شده است',
            'status': 403
        }
