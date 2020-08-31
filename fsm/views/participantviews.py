from django.core.paginator import Paginator
from rest_framework import status
from accounts.models import Member
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import TestMembersOnly

from django.contrib.contenttypes.models import ContentType

from fsm.models import *
from fsm.serializers import *
from fsm.views.functions import *
from notifications.signals import notify
from notifications.models import Notification


@transaction.atomic
@permission_classes([IsAuthenticated, TestMembersOnly ])
@api_view(['GET'])
def get_current_page(request):
    participant = request.user.participant
    page = participant.team.current_state.page
    serializer = FSMPageSerializer()
    data = serializer.to_representation(page)
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@permission_classes([IsAuthenticated, TestMembersOnly])
@api_view(['GET'])
def get_history(request):
    participant = request.user.participant
    histories = participant.team.histories.all()
    serializer = TeamHistorySerializer(histories, many=True)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@permission_classes([IsAuthenticated, TestMembersOnly])
@api_view(['POST'])
def send_answer(request):
    serializer = SubmitedAnswerPostSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    instance = serializer.create(request.data)
    participant = request.user.participant
    history = participant.team.histories.filter(state=participant.team.current_state.id)[0]
    instance.team_history = history
    instance.participant = participant
    instance.save()
    data = SubmitedAnswerSerializer(instance).data
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@permission_classes([IsAuthenticated, TestMembersOnly])
@api_view(['POST'])
def move_to_next_state(request):
    team = request.user.participant.team
    edges = FSMEdge.objects.filter(tail=team.current_state.id)
    if team.current_state.name == 'start' and edges.count() == 1:
        team_change_current_state(team, edges[0].head)
        data = FSMState.to_representation(edges[0].head)
        return Response(data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def is_not_in_later(team, state):
    return len(TeamHistory.objects.filter(team=team.id, state=state.id)) == 0

@transaction.atomic
@permission_classes([IsAuthenticated, TestMembersOnly])
@api_view(['POST'])
def set_first_current_page(request):
    team = request.user.participant.team
    serializer = SetFirstStateSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    fsm = FSM.objects.filter(id=request.data['fsm'])[0]
    state = FSMState.objects.filter(fsm=fsm, name='start')[0]
    if (team.current_state is None or team.current_state.name == 'end') and is_not_in_later(team, state):
        team_change_current_state(team, state)
        data = FSMPageSerializer().to_representation(state.page)
    else:
         return Response(" شما در کارگاه دیگری هستید یا قبلا اینجا بوده اید",status=status.HTTP_400_BAD_REQUEST)
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def request_mentor(request):
    team = request.user.participant.team
    qs = Notification.objects.filter(
        actor_content_type=ContentType.objects.get_for_model(team).id,
        actor_object_id=team.pk,
        recipient__is_mentor=True,
        unread=True
    )
    if qs.count() > 0:
        return Response({"text": "قبلا درخواست دادی. یکم بیشتر صبر کن."}, status=status.HTTP_200_OK)
    notify.send(team, recipient=Member.objects.filter(is_mentor=True), verb="request_mentor")
    return Response({"text": "درخواست ارسال شد. به زودی یکی از منتورا میاد اینجا."}, status=status.HTTP_200_OK)
