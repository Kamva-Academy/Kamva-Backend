
from fsm.models import *
from django.utils import timezone

from fsm.serializers import FSMStateSerializer, FSMStateGetSerializer, WidgetSerializer, SubmitedAnswerSerializer, \
    AnswerSerializer, PlayerFSMStateGetSerializer


def team_change_current_state(team, state):
    #fsm change checked
    #create history
    team.current_state = state
    if state and len(PlayerHistory.objects.filter(team=team.id, state=state.id)) == 0:
        history = PlayerHistory.objects.create(start_time=timezone.localtime(), team=team, state=state)
    team.save()


def user_change_current_state(participant, state):
    #TODO change_current_state body
    # check if it is in history or next state
    pass


def user_get_current_state(player, fsm):
    try:
        player_workshop = PlayerWorkshop.objects.filter(player=player, workshop=fsm)[0]
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
        widgetJson.pop('answer', None)
        widgets.append(widgetJson)

        last_answer = SubmittedAnswer.objects.filter(problem_id=widget.id, player=player)\
            .order_by('-publish_date')
        if len(last_answer) > 0:
            submitted_answer = AnswerSerializer().to_representation(last_answer[0].xanswer())
            widgetJson['last_submit'] = submitted_answer
    return widgets


def player_state(state, player):
    state_result = PlayerFSMStateGetSerializer(state).data
    widgets = current_state_widgets_json(state, player)
    state_result['widgets'] = widgets
    return state_result
