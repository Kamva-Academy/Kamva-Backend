from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType
from accounts.models import *

from fsm.models import *
from fsm.serializers import *
from fsm.views import permissions as customPermissions
from fsm.views.functions import *
from notifications.models import Notification

import logging

logger = logging.getLogger(__name__)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def edit_edges(request):
    serializer = EditEdgesSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        state = FSMState.objects.filter(id=serializer.validated_data['tail'])[0]
    except:
        return Response("state not found", status=status.HTTP_400_BAD_REQUEST)

    data = []
    ids = []
    index = 0
    for edge_data in serializer.validated_data['edges']:
        try:
            id = request.data['edges'][index]['id']
            instance = FSMEdge.objects.filter(id=id)[0]
            instance = FSMEdgeSerializer().update(instance, edge_data)
        except:
            instance = FSMEdgeSerializer().create(edge_data)
        data.append(FSMEdgeSerializer().to_representation(instance))
        ids.append(instance.id)
        index += 1
    for edge in FSMEdge.objects.filter(tail=state):
        if edge.id not in ids:
            edge.delete()
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def get_team_outward_edges(request):
    serializer = TeamUUIDSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response("team UUID problem ", status=status.HTTP_400_BAD_REQUEST)
    try:
        team = Team.objects.get(uuid=serializer.validated_data['uuid'])
        edges = team.current_state.outward_edges.all()
        output_serializer = serializers.ListField(child=FSMEdgeSerializer())
        data = output_serializer.to_representation(edges)
        return Response(data, status=status.HTTP_200_OK)
    except Team.DoesNotExist:
        return Response("team not found", status=status.HTTP_400_BAD_REQUEST)
    except AttributeError:
        return Response("team has no current_state", status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def get_team_history(request):
    serializer = GetTeamHistorySerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        team = Team.objects.filter(id=request.data['team'])[0]
    except:
        return Response("team not found", status=status.HTTP_400_BAD_REQUEST)
    history = team.histories.filter(state=team.current_state.id)[0]
    serializer = TeamHistorySerializer(history)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def submit_team(request):
    serializer = TeamHistorySubmitSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    history = PlayerHistory.objects.filter(team=validated_data['team'], state=validated_data['state'])[0]
    validated_data['start_time'] = history.start_time
    validated_data['pk'] = history.pk
    history.delete()
    history = PlayerHistory.objects.create(**validated_data)
    logger.info(
        f'mentor {request.user} changed state team {history.team.id} from {history.team.current_state.name} to {history.edge.head.name}')
    team_change_current_state(history.team, history.edge.head)
    data = TeamHistorySerializer().to_representation(history)
    return Response(data, status=status.HTTP_200_OK)


# create history auto
# get history
# clock + state

@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def go_to_team(request):
    serializer = GoToTeamSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    player_workshop = PlayerWorkshop.objects.get(pk=validated_data['player_workshop'])
    qs = Notification.objects.filter(
        actor_content_type=ContentType.objects.get_for_model(player_workshop).id,
        actor_object_id=player_workshop.pk,
        recipient__is_mentor=True
    )
    qs.mark_all_as_read()
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def workshop_players(request):
    fsm = get_object_or_404(FSM, id=request.data['fsm'])
    if fsm.fsm_p_type == "hybrid":
        player_workshops = PlayerWorkshop.objects.filter(workshop=fsm, player__player_type__iexact='TEAM')
    else:
        player_workshops = PlayerWorkshop.objects.filter(workshop=fsm)
    serializer = PlayerWorkshopSerializer(player_workshops, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def mentor_get_workshop_player(request):
    player_workshop = get_object_or_404(PlayerWorkshop, id=request.data['player_workshop'])
    serializer = MentorPlayerWorkshopSerializer(player_workshop)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def mentor_get_player_state(request):
    state = get_object_or_404(MainState, id=request.data['state'])
    if state.fsm.fsm_p_type != 'individual':
        player = get_object_or_404(Team, uuid=request.data['player_uuid'])
    else:
        player = get_participant(get_object_or_404(Member, uuid=request.data['player_uuid']))
    player_workshop = get_player_workshop(player, state.fsm)
    state_result = player_state(state, player_workshop)
    return Response(state_result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def mentor_get_all_problems(request):
    result = []
    fsms = FSM.objects.all()
    for fsm in fsms:
        states = MainState.objects.filter(fsm=fsm)
        states_result = []
        for state in states:
            problems = Problem.objects.filter(state=state).values('id', 'name')
            states_result.append({'state_id': state.id, 'state_name': state.name, 'problems': problems})
        result.append({'fsm_id': fsm.id, 'fsm_name': fsm.name, 'states': states_result})

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission])
def mentor_get_submissions(request):
    fsm_id = request.data.get('fsm_id', None)
    state_id = request.data.get('state_id', None)
    problem_id = request.data.get('problem_id', None)
    fsm = FSM.objects.filter(id=fsm_id).last()
    state = FSMState.objects.filter(id=state_id).last()
    problem = Problem.objects.filter(id=problem_id).last()

    result = []

    if fsm and state and state.fsm != fsm:
        return Response([], status=status.HTTP_400_BAD_REQUEST)
    if fsm and state and problem and problem.state != state:
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    fsms = FSM.objects.all()
    if fsm:
        fsms = fsms.filter(id=fsm.id)

    for f in fsms:
        states = MainState.objects.filter(fsm=f)
        if state:
            states = states.filter(id=state.id)

        states_result = []
        for s in states:
            problems = Problem.objects.filter(state=s)
            if problem:
                problems = problems.filter(id=problem.id)

            problems_result = []
            for p in problems:
                submitted_answers = p.submitted_answers
                submissions_result = []
                for s_a in submitted_answers:
                    if s_a.answer is None:
                        continue
                    ans = s_a.answer
                    submit_result = {'id': s_a.id,
                                     'player_id': s_a.player.id,
                                     'submission_date': s_a.publish_date,
                                     'answer_id': ans.id}
                    if ans is UploadFileAnswer:
                        submit_result['answer_file_url'] = ans.answer_file.url
                        submit_result['answer_file_name'] = ans.file_name
                    else:
                        submit_result['answer_text'] = ans.text
                    if s_a.review:
                        review = {'score': s_a.review.score,
                                  'description': s_a.description,
                                  'is_valid': s_a.is_valid}
                        submit_result['review'] = review
                    submissions_result.append(submit_result)
                problems_result.append({'problem_id': p.id, 'problem_name': p.name, 'max_score': p.max_score,
                                        'submissions': submissions_result})
            states_result.append({'state_id': s.id, 'state_name': s.name, 'problems': problems_result})
        result.append({'fsm_id': f.id, 'fsm_name': f.name, 'states': states_result})

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission])
@transaction.atomic
def mentor_mark_submission(request):
    submission_id = request.data.get('submission_id', None)
    score = request.data.get('score', None)
    description = request.data.get('description', None)
    submission = get_object_or_404(SubmittedAnswer, id=submission_id)

    if len(ScoreTransaction.objects.filter(submitted_answer=submission)) > 0:
        return Response({'error': 'this submission has already been marked'}, status=status.HTTP_400_BAD_REQUEST)

    if score is None:
        return Response({'error': 'score is required'}, status=status.HTTP_400_BAD_REQUEST)

    state = submission.problem.state
    if state is MainState:
        fsm = state.fsm
    else:
        fsm = state.state.fsm
    player_workshop = get_player_workshop(submission.player, fsm)

    if player_workshop is None:
        return Response({'error': 'Player_workshop not found'}, status=status.HTTP_404_NOT_FOUND)

    new_tr = ScoreTransaction.objects.create(score=score,
                                             player_workshop=player_workshop,
                                             description=description,
                                             is_valid=True,
                                             submitted_answer=submission)
    invalid_transactions = ScoreTransaction.objects.filter(player_workshop=player_workshop,
                                                           submitted_answer__problem=submission.problem)
    for tr in invalid_transactions:
        if tr.is_valid:
            tr.is_valid = False
    return Response({'new_score': new_tr}, status=status.HTTP_201_CREATED)
