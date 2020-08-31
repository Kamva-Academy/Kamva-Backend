from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

from fsm.models import *
from fsm.serializers import *
from fsm.views import permissions as customPermissions
from fsm.views.functions import *

@transaction.atomic
@permission_classes( [permissions.IsAuthenticated, customPermissions.MentorPermission, ])
@api_view(['POST'])
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
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
@api_view(['POST'])
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
@permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
@api_view(['POST'])
def submit_team(request):
    serializer = TeamHistorySubmitSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    history = TeamHistory.objects.filter(team=validated_data['team'], state=validated_data['state'])[0]
    validated_data['start_time'] = history.start_time
    validated_data['pk'] = history.pk
    history.delete()
    history = TeamHistory.objects.create(**validated_data)
    team_change_current_state(history.team, history.edge.head)
    data = TeamHistorySerializer().to_representation(history)
    return Response(data, status=status.HTTP_200_OK)

#create history auto
#get history
#clock + state