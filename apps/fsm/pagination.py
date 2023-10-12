from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000

class RegistrationReceiptSetPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
