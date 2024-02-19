import logging
from rest_framework.exceptions import ParseError

from apps.fsm.models import *
from apps.fsm.serializers.answer_serializers import AnswerSerializer
from apps.fsm.serializers.widget_serializers import WidgetSerializer
from errors.error_codes import serialize_error


logger = logging.getLogger(__name__)


def get_receipt(user, fsm):
    if fsm.registration_form and fsm.event.registration_form:
        raise ParseError(serialize_error('4077'))
    registration_form = fsm.registration_form or fsm.event.registration_form
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                              is_participating=True).first()


def get_player(user, fsm, receipt):
    return user.players.filter(fsm=fsm, receipt=receipt, is_active=True).first()


def move_on_edge(p, edge, departure_time, is_forward):
    p.current_state = edge.head if is_forward else edge.tail
    p.last_visit = departure_time
    p.save()
    try:
        last_state_history = PlayerHistory.objects.get(
            player=p, state=edge.tail if is_forward else edge.head, end_time=None)
    except:
        last_state_history = None
    if last_state_history:
        last_state_history.end_time = departure_time
        last_state_history.save()
    PlayerHistory.objects.create(player=p, state=edge.head if is_forward else edge.tail, entered_by_edge=edge,
                                 start_time=departure_time, reverse_enter=not is_forward)
    return p


def get_a_player_from_team(team, fsm):
    head_receipt = team.team_head
    players = Player.objects.filter(fsm=fsm, receipt__in=team.members.all())
    if len(players) <= 0:
        logger.info('no player found for any member of team')
        raise ParseError(serialize_error('4088'))
    else:
        player = players.filter(receipt=head_receipt).first()
        if not player:
            player = players.first()
        return player


def get_player_latest_taken_edge(player: Player):
    latest_history = player.histories.filter(
        reverse_enter=False, state=player.current_state).last()

    if latest_history and latest_history.entered_by_edge:
        last_taken_edge = latest_history.entered_by_edge
    else:
        # if the latest hostory is deleted, choose an inward_edges randomly
        last_taken_edge = player.current_state.inward_edges.all().first()
    return last_taken_edge


def get_scores_sum(player_workshop):
    pass
