from rest_framework import permissions
from accounts.models import Member, Team, Participant


class MentorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # print(request.user, request.user.is_authenticated, request.user.is_mentor)
        return bool(request.user and request.user.is_authenticated and request.user.is_mentor)


class TestMembersOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        try:
            if user.participant.team.is_team_active():
                return True
        except:
            return False
        return False

