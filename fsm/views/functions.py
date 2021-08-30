from django.db.models import Sum

from fsm.models import *
from django.utils import timezone

from fsm.serializers.paper_serializers import EdgeSimpleSerializer
from fsm.serializers.player_serializer import PlayerHistorySerializer
from fsm.serializers.serializers import PlayerStateGetSerializer
from fsm.serializers.widget_serializers import WidgetSerializer
from fsm.serializers.answer_serializers import AnswerSerializer
from scoring.models import ScoreTransaction

logger = logging.getLogger(__name__)


def get_receipt(user, fsm):
    if fsm.registration_form and fsm.event.registration_form:
        raise ParseError(serialize_error('4077'))
    registration_form = fsm.registration_form or fsm.event.registration_form
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                              is_participating=True).first()


def get_player(user, fsm):
    return user.players.filter(fsm=fsm, is_active=True).first()


def move_on_edge(p, edge, departure_time, is_forward):
    p.current_state = edge.head if is_forward else edge.tail
    p.last_visit = departure_time
    p.save()
    last_state_history = PlayerHistory.objects.filter(player=p, state=edge.tail if is_forward else edge.head).last()
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


def team_change_current_state(team, state):
    # fsm change checked
    # create history
    team.current_state = state
    if state and len(PlayerHistory.objects.filter(team=team.id, state=state.id)) == 0:
        history = PlayerHistory.objects.create(start_time=timezone.localtime(), team=team, state=state)
    team.save()


def user_change_current_state(participant, state):
    # TODO change_current_state body
    # check if it is in history or next state
    pass


def user_get_current_state(player, fsm):
    try:
        player_workshop = PlayerWorkshop.objects.filter(player=player, workshop=fsm).last()
        current_state = player_workshop.current_state
        if current_state is None:
            current_state = fsm.first_state
    except:
        if fsm.fsm_p_type == 'hybrid':
            return None
        PlayerWorkshop.objects.create(workshop=fsm, player=player,
                                      current_state=fsm.first_state, last_visit=timezone.now())
        current_state = fsm.first_state
    return current_state


def current_state_widgets_json(state, player):
    widgets = []
    for widget in state.widgets():
        widgetJson = WidgetSerializer().to_representation(widget)
        # widgetJson.pop('answer', None)
        widgets.append(widgetJson)

        last_answer = SubmittedAnswer.objects.filter(problem_id=widget.id, player=player) \
            .order_by('-publish_date')
        if len(last_answer) > 0:
            submitted_answer = AnswerSerializer().to_representation(last_answer[0].xanswer())
            widgetJson['last_submit'] = submitted_answer
        else:
            if 'answer' in widgetJson:
                widgetJson.pop('answer')
    return widgets


def current_state_incoming_edge(state, player_workshop):
    player_history = PlayerHistory.objects.filter(player_workshop=player_workshop, state=state).last()
    if player_history:
        edge = player_history.inward_edge
    else:
        return
    return edge


def player_state(state, player_workshop):
    state_result = PlayerStateGetSerializer(state).data
    widgets = current_state_widgets_json(state, player_workshop.player)
    state_result['widgets'] = widgets
    edge = current_state_incoming_edge(state, player_workshop)
    if edge:
        state_result['inward_edges'] = [EdgeSimpleSerializer().to_representation(edge)]
    else:
        state_result['inward_edges'] = []

    return state_result


def register_individual_workshop(workshop, participant):
    player_workshop = PlayerWorkshop.objects.create(workshop=workshop, player=participant,
                                                    current_state=workshop.first_state, last_visit=timezone.now())
    return player_workshop


def get_player_workshop(player, fsm):
    return PlayerWorkshop.objects.filter(player=player, workshop=fsm).last()


# TODO - BIGGEST TOF EVER
def get_participant(user, event="مسافر صفر"):
    current_event = Event.objects.get(name=event)
    return Participant.objects.filter(member=user, event=current_event).last()


def get_score_histories(player_workshop):
    score_transactions = ScoreTransaction.objects.filter(player_workshop=player_workshop)
    return [{'description': s.description,
             'id': s.id,
             'is_valid': s.is_valid,
             'player_workshop': s.player.id,
             'score': s.score,
             'submitted_answer': s.answer.id if s.answer is not None else None,
             'problem_name': s.answer.problem.name if (s.answer is not None) and (
                     s.answer.problem is not None) else None,
             'state_name': s.answer.problem.form.name if (s.answer is not None) and (
                     s.answer.problem is not None) else None,
             'problem_id': s.answer.problem.id if (s.answer is not None) and (
                     s.answer.problem is not None) else None} for s in score_transactions]


def get_scores_sum(player_workshop):
    sum_scores = ScoreTransaction.objects.filter(player_workshop=player_workshop, is_valid=True).aggregate(Sum('score'))
    return sum_scores.get('score__sum', 0)
