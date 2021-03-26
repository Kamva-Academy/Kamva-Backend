import json
import os

from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets

import accounts
from fsm.views import permissions as customPermissions
from accounts.models import Member, Player, Participant
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from scoring.models import ScoreTransaction
from .permissions import ParticipantPermission

from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ParseError


from fsm.models import *
from fsm.serializers import *
from fsm.views.functions import *
from notifications.signals import notify
from notifications.models import Notification

import logging
logger = logging.getLogger(__name__)


# TODO - BIGGEST TOF EVER
def get_participant(user, event="مسافر صفر"):
    current_event = Event.objects.get(name=event)
    return Participant.objects.get(member=user, event=current_event)

# @transaction.atomic
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, ParticipantPermission])
# def get_current_state(request):
#     participant = request.user.participant
#     # fsm_id = request.GET.get('fsmId')
#     if not participant.team:
#         logger.error(f'participant {request.user} is not member of any team')
#         return Response({}, status=status.HTTP_400_BAD_REQUEST)
#     if participant.team.current_state:
#         state = participant.team.current_state
#         serializer = FSMStateSerializer()
#         data = serializer.to_representation(state)
#         return Response(data, status=status.HTTP_200_OK)
#     else:
#         logger.error(f'participant d cd {request.user} : current_state is not set')
#         return Response({},status=status.HTTP_400_BAD_REQUEST)
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
@permission_classes([IsAuthenticated, ParticipantPermission])
def get_history(request):
    #TODO check this api
    player = request.data['player']
    histories = player.histories.all()
    serializer = PlayerHistorySerializer(histories, many=True)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, ParticipantPermission])
def send_answer(request):
    if request.data['problem_type'] == 'ProblemUploadFileAnswer':
        return send_pdf_answer(request)

    serializer = SubmitedAnswerPostSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    instance = serializer.create(request.data)
    # participant = request.user.participant
    # history = participant.team.histories.filter(state=participant.team.current_state.id)[0]
    # instance.team_history = history
    # instance.participant = participant
    instance.save()
    correct_answer = getattr(sys.modules[__name__], request.data['problem_type']).objects.get(id=request.data['problem']).answer
    if str(correct_answer.text) == request.data['answer']['text']:
        result = True
    else:
        result = False
    data = SubmitedAnswerSerializer(instance).data
    data['answer_result'] = result
    correct_answer = AnswerSerializer().to_representation(correct_answer)
    data['answer'] = correct_answer
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@permission_classes([IsAuthenticated, ParticipantPermission, customPermissions.MentorPermission,])
def send_pdf_answer(request):
    player = accounts.models.Player.objects.get(id=request.data['player'])
    problem = Problem.objects.get(id=request.data['problem'])
    if 'answer_file' not in request.data:
        raise ParseError("Empty content answer file")
    answer_file = request.data['answer_file']
    file_name = answer_file.name
    pasvand = file_name[file_name.rfind('.'):]
    answer_file.name = str(player.id) + "-" + str(problem.id) + str(pasvand)

    upload_file_answer = UploadFileAnswer.objects.create(
        answer_file=answer_file,
        answer_type='UploadFileAnswer',
        file_name=file_name
    )

    former_answer = SubmittedAnswer.objects.filter(
        problem=problem,
        player=player
    )
    if len(former_answer)>0:
        former_answer = former_answer[0]
        old_file = former_answer.answer.uploadfileanswer.answer_file
        former_answer.delete()
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


    instance = SubmittedAnswer.objects.create(
        problem=problem,
        answer=upload_file_answer,
        player=player,
        publish_date=timezone.localtime()
    )
    data = SubmitedAnswerSerializer(instance).data

    return Response(data)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, ParticipantPermission])
def move_to_next_state(request):
    team = get_participant(request.user).team
    edges = FSMEdge.objects.filter(tail=team.current_state.id)
    if team.current_state.name == 'start' and edges.count() == 1:
        logger.info(
            f'team {get_participant(request.user).team.id} changed state team from {team.current_state.name} to {edges[0].head.name}')
        team_change_current_state(team, edges[0].head)
        data = MainStateGetSerializer().to_representation(edges[0].head)
        return Response(data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def get_last_state_in_fsm(team, fsm):
    try:
        hist = PlayerHistory.objects.filter(team=team, state__fsm=fsm).order_by('-start_time')[0]
        return hist.state
    except IndexError:
        try:
            return MainState.objects.filter(fsm=fsm, name='start')[0]
        except IndexError:
            logger.error(f'fsm {fsm.name} has no start state')
            return None
            # return Response({}, status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated, ParticipantPermission])
def request_mentor(request):
    participant = get_participant(request.user)

    fsm = get_object_or_404(FSM, id=request.data['fsm'])
    player = get_object_or_404(accounts.models.Player, id=request.data['player'])
    player_workshop = PlayerWorkshop.objects.filter(player=player, workshop=fsm)[0]

    qs = Notification.objects.filter(
            actor_content_type=ContentType.objects.get_for_model(player_workshop).id,
        actor_object_id=player_workshop.pk,
        recipient__is_mentor=True,
        unread=True
    )
    if qs.count() > 0:
        return Response({"text": "قبلا درخواست دادی. یکم بیشتر صبر کن."}, status=status.HTTP_200_OK)
    notify.send(player_workshop, recipient=Member.objects.filter(is_mentor=True), verb="request_mentor")
    return Response({"text": "درخواست ارسال شد. به زودی یکی از منتورا میاد اینجا."}, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated,])
# def get_team_fsm_history(request):
#     user = request.user
#     par = user.participant
#     serializer = GetTeamHistorySerializer(data=request.data)
#     if not serializer.is_valid(raise_exception=True):
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#     try:
#         team = Team.objects.filter(id=request.data['team'])[0]
#         if par.team != team:
#             return Response("you can not see other team's history", status=status.HTTP_403_FORBIDDEN)
#     except:
#         return Response("team not found",status=status.HTTP_400_BAD_REQUEST)
#     try:
#         fsm = FSM.objects.get(id=request.data['fsm'])
#     except:
#         return Response("FSM not found",status=status.HTTP_400_BAD_REQUEST)
#     histories = PlayerHistory.objects.filter(team=team, state__fsm=fsm).order_by('start_time')
#     json_result = []
#     for history in histories:
#         serializer = TeamHistorySerializer(history)
#         data = serializer.data
#         data['state_name'] = history.state.name
#         json_result.append(data)
#     return Response(json_result, status=status.HTTP_200_OK)

# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated,])
# def team_go_back_to_state(request):
#     team = Team.objects.get(id=request.data['team'])
#     state = FSMState.objects.get(id=request.data['state'])
#     try:
#         history = TeamHistory.objects.filter(team=team, state=state)[0]
#     except:
#         return Response({"error": "state is not in history"}, status=status.HTTP_400_BAD_REQUEST)
#
#     team_change_current_state(team, state)
#     data = FSMStateSerializer().to_representation(state)
#     return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def player_go_forward_on_edge(request):
    edge = request.data['edge']
    player = request.data['player']
    player1 = get_object_or_404(Player, id=player)

    edge = get_object_or_404(FSMEdge, id=edge)
    fsm = edge.tail.fsm
    if fsm.fsm_p_type == 'hybrid':
        player = get_participant(request.user)
    else:
        player = player1

    playerWorkshop = PlayerWorkshop.objects.filter(player=player, workshop=fsm).last()
    logger.info(
        f'player in {playerWorkshop.current_state.name} trying to changed state from {edge.tail.name} to {edge.head.name}')

    if playerWorkshop.current_state == edge.tail:

        playerWorkshop.current_state = edge.head
        playerWorkshop.last_visit = timezone.now()
        playerWorkshop.save()

        # player history management
        # last_state_history = PlayerHistory.objects.filter(player=player, state=edge.tail).last()
        # last_state_history.end_time = timezone.now()
        # last_state_history.save()
        # PlayerHistory.objects.create(player=player, edge=edge, start_time=timezone.now(), state=edge.head)
    else:
        logger.warning(
            f'illegal transmission - player in {playerWorkshop.current_state.name} trying to changed state from {edge.tail.name} to {edge.head.name}')

        state_result = player_state(playerWorkshop.current_state, player)
        state_result['error'] = "transmission is not accessable from this state"
        return Response(state_result,
                          status=status.HTTP_400_BAD_REQUEST)

    state_result = player_state(playerWorkshop.current_state, player)
    return Response(state_result, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def player_go_backward_on_edge(request):
    edge = request.data['edge']
    player = request.data['player']

    edge = get_object_or_404(FSMEdge, id=edge)
    fsm = edge.tail.fsm
    if fsm.fsm_p_type == 'hybrid':
        player = get_participant(request.user)
    else:
        player = get_object_or_404(Player, id=player)

    playerWorkshop = PlayerWorkshop.objects.filter(player=player, workshop=fsm).last()
    logger.info(
        f'player in {playerWorkshop.current_state.name} trying to changed state from {edge.tail.name} to {edge.head.name}')

    if not edge.is_back_enabled:
        state_result = player_state(playerWorkshop.current_state, player)
        state_result['error'] = "امکان برگشت به عقب در این گام وجود ندارد."
        return Response(state_result,
                        status=status.HTTP_400_BAD_REQUEST)

    if playerWorkshop.current_state == edge.head:
        playerWorkshop.current_state = edge.tail
        playerWorkshop.last_visit = timezone.now()
        playerWorkshop.save()
        # TODO set the current player history based on your need
        # PlayerHistory.objects.create(player=player, edge=edge, start_time=timezone.now(), state= edge.head)
    else:
        logger.warning(
            f'illegal transmission - player in {playerWorkshop.current_state.name} trying to changed state from {edge.tail.name} to {edge.head.name}')

        state_result = player_state(playerWorkshop.current_state, player)
        state_result['error'] = "transmission is not accessible from this state"
        return Response(state_result,
                        status=status.HTTP_400_BAD_REQUEST)

    state_result = player_state(playerWorkshop.current_state, player)
    return Response(state_result, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def user_get_team_outward_edges(request):
    state = MainState.objects.get(id=request.data['state'])
    serializer = TeamUUIDSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        team = Team.objects.get(uuid=serializer.validated_data['uuid'])
        if state != team.current_state:
            return Response("this state is not the team's current state", status=status.HTTP_400_BAD_REQUEST)
        # if state.type == str(StateType.withMentor):
        #     return Response("this state with mentor and user doesn't have permission to get forward edges", status=status.HTTP_403_FORBIDDEN)

        edges = team.state.outward_edges.all()
        output_serializer = serializers.ListField(child=FSMEdgeSerializer())
        data = output_serializer.to_representation(edges)
        return Response(data, status=status.HTTP_200_OK)
    except Team.DoesNotExist:
        return Response("team not found", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ParticipantPermission])
def user_workshops(request):
    participant = get_participant(request.user)
    if request.method == 'GET':
        individual_workshops = FSM.objects.filter(players=participant)
        if participant.team_set.count() > 0:
            for team in participant.team_set.all():
                team_workshops = FSM.objects.filter(players=team)
        workshops = (team_workshops|individual_workshops).distinct()
        serializer = FSMSerializer(workshops, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ParticipantPermission])
def get_player_current_state(request):
    fsm = request.data['fsm']
    fsm = FSM.objects.get(id=fsm)
    player1 = request.data['player']
    if fsm.fsm_p_type == 'hybrid':
        player = get_participant(request.user)
    else:
        player = player1
        player = accounts.models.Player.objects.get(id=player)

    current_state = user_get_current_state(player, fsm)
    # result = current_state_json(current_state)
    # serializer = FSMStateGetSerializer(current_state)
    if fsm.fsm_p_type == 'hybrid' and current_state is None:
        team = request.data['player']
        team = accounts.models.Team.objects.get(id=team)
        PlayerWorkshop.objects.create(workshop=fsm, player=team,
                                      current_state=fsm.first_state, last_visit=timezone.now())
        current_state = fsm.first_state
        for member in team.team_participants.all():
            if len(PlayerWorkshop.objects.filter(player=member, workshop=fsm)) == 0:
                PlayerWorkshop.objects.create(workshop=fsm, player=member,
                                          current_state=current_state, last_visit=timezone.now())
    result = PlayerStateGetSerializer(current_state).data
    widgets = current_state_widgets_json(current_state, player1)
    result['widgets'] = widgets


    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ParticipantPermission])
def start_workshop(request):

    fsm = request.data['fsm']
    fsm = get_object_or_404(FSM, id=fsm)
    if fsm.lock and len(fsm.lock) > 0:
        key = request.data.get('key', None)
        if key:
            if key != fsm.lock:
                return Response({"error": "کلیدتون به این قفل نمی‌خوره! لطفا کلید معتبری وارد کنید."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "این کارگاه قفل دارد؛ لطفا کلیدی وارد کنید."},
                            status=status.HTTP_400_BAD_REQUEST)

    fsm_type = fsm.fsm_p_type
    if fsm_type == 'hybrid':
        player = get_participant(request.user)
        try:
            player_workshop = PlayerWorkshop.objects.filter(
                workshop=fsm,
                player__player_type='TEAM',
                player__team__team_participants=player
            )[0]
            # try:
            #     history = PlayerHistory.objects.get(player=player, state=fsm.first_state)
            # except PlayerHistory.DoesNotExist:
            #     PlayerHistory.objects.create(
            #         player=player,
            #         state=fsm.first_state,
            #         start_time=timezone.now(),
            #         edge=None
            #     )
        except:
            return Response({"error": "این کاربر در این کارگاه ثبت‌نام نکرده."}, status=status.HTTP_400_BAD_REQUEST)
        # current_state = user_get_current_state(player, fsm)
        player_data = PlayerSerializer().to_representation(player_workshop.player)
    elif fsm_type == 'team':
        player = get_participant(request.user)
        try:
            player_workshop = PlayerWorkshop.objects.filter(
                workshop=fsm,
                player__player_type='TEAM',
                player__team__team_participants=player
            ).last()
            logger.info(f'salam, {player_workshop}')
            history = PlayerHistory.objects.filter(player_workshop=player_workshop).last()
            if not history:
                PlayerHistory.objects.create(
                    player_workshop=player_workshop,
                    state=fsm.first_state,
                    start_time=timezone.now(),
                    edge=None
                )
        except:
            return Response({"error": "این کاربر در این کارگاه ثبت‌نام نکرده."}, status=status.HTTP_400_BAD_REQUEST)
        # current_state = player_workshop.current_state
        player_data = PlayerSerializer().to_representation(player_workshop.player)
        score = ScoreTransaction.objects.filter(player_workshop=player_workshop).aggregate(Sum('score'))
        player_workshop_id = player_workshop.id

    elif fsm_type == 'individual':
        player = get_participant(request.user)
        try:
            player_workshop = PlayerWorkshop.objects.get(player=player, workshop=fsm)
        except PlayerWorkshop.DoesNotExist:
            PlayerWorkshop.objects.create(
                player=player, workshop=fsm,
                current_state=fsm.first_state,
                last_visit=timezone.now())
        # try:
        #     history = PlayerHistory.objects.get(player=player, state=fsm.first_state)
        # except PlayerHistory.DoesNotExist:
        #     PlayerHistory.objects.create(
        #         player=player,
        #         state=fsm.first_state,
        #         start_time=timezone.now(),
        #         edge=None
        #     )
        # current_state = user_get_current_state(player, fsm).data
        # current_state = FSMStateGetSerializer(current_state).data
        player_data = PlayerSerializer().to_representation(player)
    else:
        return Response({'error': 'fsm type is bad'}, status=status.HTTP_400_BAD_REQUEST)

    result = {'player': player_data, 'player_workshop_id': player_workshop_id, 'score': score}
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ParticipantPermission])
def participant_get_player_state(request):
    participant = get_participant(request.user)
    state = get_object_or_404(MainState, id=request.data['state'])
    if state.fsm.fsm_p_type == "TEAM":
        player = get_object_or_404(Team, uuid=request.data['player_uuid'])
    else:
        player = participant
    if player.player_type == "TEAM":
        if not (participant in player.team.team_participants.all()):
            return Response({"error":"شرکت‌کننده‌ها نمی‌توانند استیت یک شرکت‌کننده‌ی دیگر را بگیرند."}, status=status.HTTP_403_FORBIDDEN)
    else:
        if not (player == participant):
            return Response({"error":"شرکت‌کننده‌ها نمی‌توانند استیت یک شرکت‌کننده‌ی دیگر را بگیرند."}, status=status.HTTP_403_FORBIDDEN)
    state_result = player_state(state, player)
    return Response(state_result)


