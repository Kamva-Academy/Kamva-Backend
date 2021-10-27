from django.shortcuts import get_object_or_404
from rest_framework import permissions
from accounts.models import Member, Teamm, Participant
from fsm.models import RegistrationReceipt, Event, RegistrationForm, FSM


class IsEventModifier(permissions.BasePermission):
    """
    Permission for evet's admin to update event
    """
    message = 'You are not this event\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.modifiers


def is_form_modifier(form, user):
    return (form.event_or_fsm and user in form.event_or_fsm.modifiers) or user == form.creator


class IsRegistrationFormModifier(permissions.BasePermission):
    """
    Permission for form's admin to update form
    """
    message = 'You are not this registration_form\'s modifier'

    def has_object_permission(self, request, view, obj):
        return is_form_modifier(obj, request.user)


class IsCertificateTemplateModifier(permissions.BasePermission):
    """
    Permission for certificate template modifiers
    """

    message = 'You are not this certificate template\'s registration_form modifier'

    def has_object_permission(self, request, view, obj):
        form = obj.registration_form
        return form and is_form_modifier(form, request.user)


class IsRegistrationReceiptOwner(permissions.BasePermission):
    """
    Permission for registration receipt owner to get
    """
    message = 'You are not this registration receipt\'s owner'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsReceiptsFormModifier(permissions.BasePermission):
    """
    Permission for receipt's registration form modifiers
    """
    message = 'You are not this registration receipt\'s registration form modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.answer_sheet_of.event_or_fsm.modifiers


class IsTeamHead(permissions.BasePermission):
    """
    Permission for team's head
    """
    message = 'You are not this team\'s head'

    def has_object_permission(self, request, view, obj):
        return obj.team_head.user == request.user


class IsInvitationInvitee(permissions.BasePermission):
    """
    Permission for invitation's invitee
    """
    message = 'you are not this invitation\'s invitee'

    def has_object_permission(self, request, view, obj):
        return obj.invitee.user == request.user


class IsTeamMember(permissions.BasePermission):
    """
    Permission for team's members
    """
    message = 'you are not a member of this team'

    def has_object_permission(self, request, view, obj):
        return len(obj.members.filter(user=request.user)) == 1


class MentorPermission(permissions.BasePermission):
    """
    Permission for mentor
    """
    message = 'you are not a mentor of this fsm'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.mentors.all()


class PlayerViewerPermission(permissions.BasePermission):
    """
    Permission for viewing player
    """
    message = 'you don\'t have necessary access to view this player'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.fsm.mentors.all()


class IsStateModifier(permissions.BasePermission):
    """
    Permission for mentors modifying states
    """
    message = 'you are not this state\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.fsm.mentors.all()


class IsHintModifier(permissions.BasePermission):
    """
    Permission for mentors modifying hints
    """
    message = 'you are not this hint\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.reference.fsm.mentors.all()


class IsEdgeModifier(permissions.BasePermission):
    """
    Permission for mentors modifying edges
    """
    message = 'you are not this edge\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.tail.fsm.mentors.all() or request.user in obj.head.fsm.mentors.all()


class IsAnswerModifier(permissions.BasePermission):
    """
    Permission for modifying answers
    """
    message = 'you are not this answer\'s modifier'

    def has_object_permission(self, request, view, obj):
        if request.user == obj.submitted_by:
            return True
        if obj.problem is not None and obj.problem.paper is not None and obj.problem.paper is not None \
                and obj.problem.paper.players is not None:
            submitted_by = obj.problem.paper.players.filter(user=obj.submitted_by).first()
            if submitted_by.team and submitted_by.team.members.filter(user=request.user).first():
                return True
        return False


class HasActiveRegistration(permissions.BasePermission):
    """
    Permission for checking registration of users in events / fsms
    """
    message = 'you don\'t have an active registration receipt for this entity'

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Event):
            return len(RegistrationReceipt.objects.filter(user=request.user, answer_sheet_of=obj.registration_form,
                                                          is_participating=True)) > 0
        elif isinstance(obj, FSM):
            if obj.event:
                return len(
                    RegistrationReceipt.objects.filter(user=request.user, answer_sheet_of=obj.event.registration_form,
                                                       is_participating=True)) > 0
            else:
                return len(
                    RegistrationReceipt.objects.filter(user=request.user, answer_sheet_of=obj.registration_form,
                                                       is_participating=True))

        # -------------


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
