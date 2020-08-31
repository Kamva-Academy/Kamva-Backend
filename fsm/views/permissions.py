from rest_framework import permissions
from accounts.models import Member, Team, Participant


class MentorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        print(request.user)
        return bool(request.user and request.user.is_authenticated and request.user.is_mentor)