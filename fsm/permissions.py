from rest_framework import permissions
from accounts.models import Member, Teamm, Participant


class IsEventModifier(permissions.BasePermission):
    """
    Permission for event's admin to update event
    """
    message = 'You are not this event\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.modifiers


class IsRegistrationFormModifier(permissions.BasePermission):
    """
    Permission for event's admin to update event
    """
    message = 'You are not this registration_form\'s modifier'

    def has_object_permission(self, request, view, obj):
        return (obj.event_or_fsm and request.user in obj.event_or_fsm.modifiers) or request.user == obj.creator


class IsTeamHead(permissions.BasePermission):
    """
    Permission for team's head
    """
    message = 'You are not this team\'s head'

    def has_object_permission(self, request, view, obj):
        return obj.team_head.user == request.user


class IsTeamMember(permissions.BasePermission):
    """
    Permission for team's members
    """
    pass
# -------------


class MentorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # print(request.user, request.user.is_authenticated, request.user.is_mentor)
        return bool(request.user and request.user.is_authenticated and request.user.is_mentor)


class ParticipantPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        try:
            if user.is_participant:
                return True
        except:
            return False
        return False


class ActiveTeamsPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # user = request.user
        # try:
        #     if user.participant.team.is_team_active():
        #         return True
        # except:
        #     return False
        # return False
        return True


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.creator == request.user
