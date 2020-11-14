from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from fsm.models import *
from fsm.serializers import *
from fsm.views import permissions as customPermissions
from fsm.views.functions import *
from notifications.models import Notification

import logging
logger = logging.getLogger(__name__)


@transaction.atomic
@api_view(['POST'])
@permission_classes( [permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def edit_edges(request):
    serializer = EditEdgesSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        state = FSMState.objects.filter(id=serializer.validated_data['tail'])[0]
    except:
        return Response("state not found",status=status.HTTP_400_BAD_REQUEST)
    
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
        index +=1
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
        return Response("team not found",status=status.HTTP_400_BAD_REQUEST)
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
    logger.info(f'mentor {request.user} changed state team {history.team.id} from {history.team.current_state.name} to {history.edge.head.name}')
    team_change_current_state(history.team, history.edge.head)
    data = TeamHistorySerializer().to_representation(history)
    return Response(data, status=status.HTTP_200_OK)

#create history auto
#get history
#clock + state

@transaction.atomic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
def go_to_team(request):
    serializer = GoToTeamSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    team = Team.objects.get(pk=validated_data['team'])
    qs = Notification.objects.filter(
        actor_content_type=ContentType.objects.get_for_model(team).id,
        actor_object_id=team.pk,
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
    # TODO: add time to api
    else:
        player_workshops = PlayerWorkshop.objects.filter(workshop=fsm)
    serializer = PlayerWorkshopSerializer(player_workshops, many=True)
    return Response(serializer.data)




