import datetime
from rest_framework import permissions

from apps.fsm.models import RegistrationReceipt, State
from apps.question_widget.models import Question


class CanSubmitAnswer(permissions.BasePermission):
    """
    Permission to check whether user can submit an answer to this widget or not.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Question):
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
            return True
        else:
            return False
