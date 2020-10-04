from django.core.paginator import Paginator
from rest_framework import status, permissions
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

import logging
logger = logging.getLogger(__name__)

@transaction.atomic
@api_view(['GET'])
@permission_classes([IsAuthenticated, TestMembersOnly])
def get_current_page(request):
    participant = request.user.participant
    # fsm_id = request.GET.get('fsmId')
    if not participant.team:
        logger.error(f'participant {request.user} is not member of any team')
        return Response({},status=status.HTTP_400_BAD_REQUEST)
    if participant.team.current_state:
        page = participant.team.current_state.page
        serializer = FSMPageSerializer()
        data = serializer.to_representation(page)
        return Response(data, status=status.HTTP_200_OK)
    else:
        logger.error(f'participant d cd {request.user} : current_state is not set')
        return Response({},status=status.HTTP_400_BAD_REQUEST)
    # try:
    #     fsm = FSM.objects.get(id=fsm_id)
    #     state = get_last_state_in_fsm(participant.team, fsm)
    #     page = state.page
    #     serializer = FSMPageSerializer()
    #     participant.team.current_state = state
    #     participant.team.save()
    #     data = serializer.to_representation(page)
    #     return Response(data, status=status.HTTP_200_OK)
    # except:
    #     return Response({}, status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['GET'])
@permission_classes([IsAuthenticated, TestMembersOnly])
def get_history(request):
    #TODO get history for individual
    participant = request.user.participant
    histories = participant.team.histories.all()
    serializer = TeamHistorySerializer(histories, many=True)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, TestMembersOnly])
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
    correct_answer = getattr(sys.modules[__name__], request.data['problem_type']).objects.get(id = request.data['problem']).answer
    if correct_answer.text == request.data['answer']['text']:
        result = True
    else:
        result = False
    data = SubmitedAnswerSerializer(instance).data
    data['result']= result
    correct_answer = AnswerSerializer().to_representation(correct_answer)
    data['correct_answer'] = correct_answer
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, TestMembersOnly])
def move_to_next_state(request):
    team = request.user.participant.team
    edges = FSMEdge.objects.filter(tail=team.current_state.id)
    if team.current_state.name == 'start' and edges.count() == 1:
        logger.info(
            f'team {request.user.participant.team.id} changed state team from {team.current_state.name} to {edges[0].head.name}')
        team_change_current_state(team, edges[0].head)
        data = FSMStateSerializer().to_representation(edges[0].head)
        return Response(data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def is_not_in_later(team, state):
    return len(TeamHistory.objects.filter(team=team.id, state=state.id)) == 0


def get_last_state_in_fsm(team, fsm):
    try:
        hist = TeamHistory.objects.filter(team=team, state__fsm=fsm).order_by('-start_time')[0]
        return hist.state
    except IndexError:
        try:
            return FSMState.objects.filter(fsm=fsm, name='start')[0]
        except IndexError:
            logger.error(f'fsm {fsm.name} has no start state')
            return None
            # return Response({}, status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, TestMembersOnly])
def set_first_current_page(request):
    team = request.user.participant.team
    serializer = SetFirstStateSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    fsm = FSM.objects.filter(id=request.data['fsm'])[0]
    if (team.current_state is None or team.current_state.name == 'end'):
        state = get_last_state_in_fsm(team, fsm)
        try:
            logger.info(
                f'changed state team {team.id} from {team.current_state.name} to {state.name}')
        except:
            if state:
                logger.info(
                    f'changed state team {team.id} from None to {state.name}')
            elif not team.current_state:
                logger.info(
                    f'changed state team {team.id} from {team.current_state.name} to None')
        team_change_current_state(team, state)
        data = FSMPageSerializer().to_representation(state.page)
    else:
         return Response("شما در کارگاه دیگری هستید!",status=status.HTTP_400_BAD_REQUEST)
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, TestMembersOnly])
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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
def get_team_fsm_history(request):
    user = request.user
    par = user.participant
    serializer = GetTeamHistorySerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        team = Team.objects.filter(id=request.data['team'])[0]
        if par.team != team:
            return Response("you can not see other team's history", status=status.HTTP_403_FORBIDDEN)
    except:
        return Response("team not found",status=status.HTTP_400_BAD_REQUEST)
    try:
        fsm = FSM.objects.get(id=request.data['fsm'])
    except:
        return Response("FSM not found",status=status.HTTP_400_BAD_REQUEST)
    histories = TeamHistory.objects.filter(team=team, state__fsm=fsm).order_by('start_time')
    json_result = []
    for history in histories:
        serializer = TeamHistorySerializer(history)
        data = serializer.data
        data['state_name'] = history.state.name
        json_result.append(data)
    return Response(json_result, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
def team_go_back_to_state(request):
    team = Team.objects.get(id=request.data['team'])
    state = FSMState.objects.get(id=request.data['state'])
    try:
        history = TeamHistory.objects.filter(team=team, state=state)[0]
    except:
        return Response({"error": "state is not in history"}, status=status.HTTP_400_BAD_REQUEST)

    team_change_current_state(team, state)
    data = FSMStateSerializer().to_representation(state)
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def team_go_forward(request):
    serializer = TeamHistoryGoForwardSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    state = validated_data['state']
    if state.type == str(StateType.withMentor):
        return Response({"error": "state type should be without menter"}, status=status.HTTP_400_BAD_REQUEST)

    history = TeamHistory.objects.filter(team=validated_data['team'], state=validated_data['state'])[0]
    validated_data['start_time'] = history.start_time
    validated_data['pk'] = history.pk
    history.delete()
    history = TeamHistory.objects.create(**validated_data)
    logger.info(f'mentor {request.user} changed state team {history.team.id} from {history.team.current_state.name} to {history.edge.head.name}')
    team_change_current_state(history.team, history.edge.head)
    data = TeamHistorySerializer().to_representation(history)
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def user_get_team_outward_edges(request):
    state = FSMState.objects.get(id=request.data['state'])
    serializer = TeamUUIDSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        team = Team.objects.get(uuid=serializer.validated_data['uuid'])
        if state != team.current_state:
            return Response("this state is not the team's current state", status=status.HTTP_400_BAD_REQUEST)
        if state.type == str(StateType.withMentor):
            return Response("this state with mentor and user doesn't have permission to get forward edges", status=status.HTTP_403_FORBIDDEN)

        edges = team.state.outward_edges.all()
        output_serializer = serializers.ListField(child=FSMEdgeSerializer())
        data = output_serializer.to_representation(edges)
        return Response(data, status=status.HTTP_200_OK)
    except Team.DoesNotExist:
        return Response("team not found", status=status.HTTP_400_BAD_REQUEST)

