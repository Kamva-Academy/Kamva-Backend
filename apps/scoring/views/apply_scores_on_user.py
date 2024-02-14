from rest_framework.decorators import api_view

from django.db import transaction
from apps.scoring.models import Transaction
from apps.scoring.views.transaction_view import get_user_current_scores
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error


@api_view(["POST"])
@transaction.atomic
def apply_scores_on_user_view(request):
    # _apply_scores()
    pass


@transaction.atomic
def apply_cost(cost, user, cause_title, cause_description):
    if not cost:
        return
    cost_scores = cost.value

    # check if has not enough score:
    user_current_scores = get_user_current_scores(user, -1)
    print("ccccccc", user_current_scores, cost_scores)
    if not does_contain(user_current_scores, cost_scores):
        raise ParseError(serialize_error('6001'))
    
    _apply_scores(user, _reverse_scores(cost_scores),
                  cause_title, cause_description)


@transaction.atomic
def apply_reward(reward, user, cause_title, cause_description):
    if not reward:
        return

    _apply_scores(user, reward.value, cause_title,  cause_description)


def _apply_scores(user, scores, title, description):
    transaction = Transaction(to=user, value=scores, description=description)
    transaction.save()
    pass


def _reverse_scores(scores):
    reversed_scores = {}
    for key in scores:
        value = scores[key]
        reversed_scores[key] = -value
    return reversed_scores


def does_contain(scores1, scores2):
    scores = {}
    for score_type_name in scores1:
        scores[score_type_name] = scores1[score_type_name]
    for score_type_name in scores2:
        if score_type_name in scores1:
            scores[score_type_name] -= scores2[score_type_name]
        elif scores2[score_type_name] > 0:
            return False
    for score_type_name in scores:
        if scores[score_type_name] < 0:
            return False
    return True
