from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from fsm.models import *
from fsm.serializers import *

@transaction.atomic
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_current_page(request):
    participant = request.user.participant
    page = participant.team.current_state.page
    serializer = FSMPageSerializer()
    data = serializer.to_representation(page)
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_history(request):
    participant = request.user.participant
    histories = participant.team.histories.all()
    serializer = TeamHistorySerializer(histories, many=True)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)

@transaction.atomic
@permission_classes([IsAuthenticated])
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

