from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class InternalServerError(APIException):
    status_code = 500
    default_detail = 'An Internal server error occurred, please contact us.'
    default_code = 'internal_server_error'
