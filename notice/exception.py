from rest_framework import status
from rest_framework.exceptions import APIException


class NoResult(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'no result'
    default_code = 'NO_RESULT'


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ''
    default_code = 'BAD_REQUEST'
