
from rest_framework import permissions
from apps.fsm.models import RegistrationForm, State


def is_form_modifier(form, user):
    return (form.event_or_fsm and user in form.event_or_fsm.modifiers) or user == form.creator


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


class IsAnswerModifier(permissions.BasePermission):
    """
    Permission for modifying answers
    """
    message = 'you are not this answer\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.submitted_by
