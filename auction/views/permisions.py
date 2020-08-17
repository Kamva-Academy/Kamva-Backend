from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.utils import timezone

from mhbank.models import Question, Account, Answer, Guidance
import datetime

"""
POST = ADD NEW ONE
PUT = CHANGE
GET = READ
DELET = DELET
"""
class BidPermission(BasePermission):
    def has_permission(self, request, view):
        return True