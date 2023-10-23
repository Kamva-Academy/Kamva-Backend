import json
from rest_framework import status
from rest_framework.response import Response

from rest_framework.response import Response
from rest_framework.decorators import api_view
from apps.fsm.views.fsm_view import _get_fsm_edges

from apps.roadmap.models import Link
from apps.fsm.models import FSM, Player, PlayerHistory, State
from apps.roadmap.serializers import LinkSerializer


@api_view(["POST"])
def get_player_taken_path(request):
    player_id = request.data.get('player_id', None)
    taken_path: list[Link] = _get_player_taken_path(player_id)
    return Response(data=LinkSerializer(taken_path, many=True).data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_fsm_roadmap(request):
    print(request.data)
    fsm_id = request.data.get('fsm_id', None)
    fsm_roadmap = _get_fsm_roadmap(fsm_id)
    return Response(data=LinkSerializer(fsm_roadmap, many=True).data, status=status.HTTP_200_OK)


def _get_fsm_roadmap(fsm_id: int):
    fsm = FSM.get_fsm(fsm_id)
    print(fsm_id)
    edges = _get_fsm_edges(fsm)
    links = [Link.get_link_from_states(
        edge.tail, edge.head) for edge in edges]
    return links


def _get_player_taken_path(player_id: int):
    player = Player.get_player(player_id)
    player_current_state: State = player.current_state
    fsm = player_current_state.fsm
    histories: list[PlayerHistory] = player.histories.all()
    taken_path: list[Link] = []

    # 100 is consumed as maximum length in a fsm graph
    for i in range(100):
        if player_current_state == fsm.first_state:
            break

        previous_state = _get_previous_taken_state(
            player_current_state, histories)
        taken_path.append(Link.get_link_from_states(
            previous_state, player_current_state))
        player_current_state = previous_state

    return taken_path


def _get_previous_taken_state(player_current_state: State, histories: list[PlayerHistory]):
    for history in histories:
        if history.entered_by_edge.head == player_current_state:
            return history.entered_by_edge.tail
    return Exception("last state does not found")
