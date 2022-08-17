from datetime import timezone, datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from fsm.models import RegistrationReceipt, Event, RegistrationForm, FSM, Problem, State, Team


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


class IsArticleModifier(permissions.BasePermission):
    """
    Permission for editing an article
    """
    message = 'You are not this article\'s modifier'

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsTeamModifier(permissions.BasePermission):
    """
    Permission for team's modifier
    """
    message = 'You are not this team\'s modifier (event owner/team head)'

    def has_object_permission(self, request, view, obj):
        head = obj.team_head
        if head:
            return obj.team_head.user == request.user
        fsm_modifiers = obj.registration_form.event_or_fsm.modifiers
        if request.user in fsm_modifiers:
            return True
        return False


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


class MentorCorrectionPermission(permissions.BasePermission):
    """
    Permission for mentor correcting answers
    """
    message = 'you can\'t correct this answer'

    def has_object_permission(self, request, view, obj):
        if isinstance(obj.problem.paper, State):
            return request.user in obj.problem.paper.fsm.mentors.all()
        elif isinstance(obj.problem.paper, RegistrationForm):
            return is_form_modifier(obj.problem.paper, request.user)
        else:
            return request.user.is_staff or request.user.is_superuser


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
        return request.user == obj.submitted_by


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


class CanAnswerWidget(permissions.BasePermission):
    """
    Permission to check whether user can submit an answer to this widget or not.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Problem):
            if isinstance(obj.paper, State):
                registration_form = obj.paper.fsm.registration_form or obj.paper.fsm.event.registration_form
                receipt = RegistrationReceipt.objects.filter(answer_sheet_of=registration_form, user=request.user,
                                                             is_participating=True).first()
                if receipt is not None:
                    if len(receipt.players.filter(fsm=obj.paper.fsm, current_state=obj.paper)) < 1:
                        return False
                else:
                    return False

            if (obj.paper.since and datetime.now(obj.paper.since.tzinfo) < obj.paper.since) or \
                    (obj.paper.till and datetime.now(obj.paper.till.tzinfo) > obj.paper.till):
                return False

            # TODO - check for max corrections
            if obj.max_corrections:
                pass
                # if isinstance(obj.paper, State):
                #     registration_form = obj.paper.fsm.registration_form or obj.paper.fsm.event.registration_form
                #     team = Team.objects.filter(registration_form=registration_form, members__user=request.user).first()
                #     teammates = team.members.values_list('user', flat=True) if team is not None else [request.user]
                #     if len(Corrections.objects.filter(answer__problem=obj, answer__submitted_by__in=teammates) > obj.max_corrections:
                #         return False
            return True
        else:
            return False

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
