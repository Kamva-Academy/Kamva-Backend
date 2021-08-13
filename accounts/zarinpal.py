import logging

from django.conf import settings
from rest_framework.response import Response
from zeep import Client

from errors.error_codes import serialize_error
from errors.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


ZARINPAL_CONFIG = settings.ZARINPAL_CONFIG


def send_request(amount, description, callback_url, email=None, mobile=None):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    result = client.service.PaymentRequest(ZARINPAL_CONFIG['MERCHANT'], amount, description, email, mobile, callback_url)
    if result.Status == 100:
        return f'{ZARINPAL_CONFIG["ROUTE_START_PAY"]}{str(result.Authority)}'
    else:
        logger.error(f'Zarinpal send request error: {result}')
        raise ServiceUnavailable(serialize_error('5001'))


def verify(status, authority, amount):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    if status == 'OK':
        result = client.service.PaymentVerification(ZARINPAL_CONFIG['MERCHANT'], authority, amount)
        if result.Status == 100:
            logger.info(f'Transaction success: {result}')
            return {
                'message': 'Success',
                'ref_id': str(result.RefID),
                'status': 200
            }
        elif result.Status == 101:
            logger.warning(f'Transaction submitted: {result}')
            return {
                'message': 'Repetitious',
                'ref_id': str(result.RefID),
                'status': 201
            }
        else:
            logger.warning(f'Zarinpal verification error: {result}')
            return {
                'message': 'Failed',
                'status': 400
            }
    else:
        logger.warning(f'Transaction failed or canceled by authority: {authority}')
        return {
            'message': 'Failed or canceled',
            'status': 403
        }
