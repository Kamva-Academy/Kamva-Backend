from rest_framework import permissions
from accounts.models import Member, Team, Participant
import logging
logger = logging.getLogger(__name__)


class MentorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        logger.debug(f'user {request.user} has permission')
        return request.user.is_mentor
