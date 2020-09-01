from rest_framework import permissions
from accounts.models import Member, Team, Participant


class MentorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # print(request.user, request.user.is_authenticated, request.user.is_mentor)
        return bool(request.user and request.user.is_authenticated and request.user.is_mentor)


class TestMembersOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # user = request.user
        # username = user.username
        # print(request.user)
        # if username.startswith("TEST_") or user.is_mentor:
        #     return True
        # return False
        return True
