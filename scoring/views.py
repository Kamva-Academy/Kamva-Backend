from django.shortcuts import render

# Create your views here.
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from fsm.views import permissions as custom_permissions
from .serializers import ScoreSerializer, ScoreboardSerializer, ScoreTransaction
from .exception import BadRequest, ScoreTransactionNotFound
from .models import ScoreTransaction
from fsm.models import PlayerWorkshop


DEFAULT_PAGE_SIZE = 16


class ScoringAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated, custom_permissions.MentorPermission]

    """
    POST : {"player_workshop_id": 1071, "score": 20.54, "description": "solve state 5"}
    """
    def post(self, request):
        serialized = ScoreSerializer(data=request.data)
        if not serialized.is_valid():
            raise BadRequest(serialized.errors)
        result = serialized.create(serialized.validated_data)
        return Response(data={"id": result.id}, status=HTTP_200_OK)

    """
    PUT : {"id" : 12, "player_workshop_id": 1071, "score": 20.54, "description": "solve state 5"}
    """
    def put(self, request, transaction_id):
        try:
            score_transaction = ScoreTransaction.objects.get(id=transaction_id)
        except ScoreTransaction.DoesNotExist:
            raise ScoreTransactionNotFound
        serialized = ScoreSerializer(score_transaction, data=request.data, partial=True)
        if not serialized.is_valid():
            raise BadRequest(serialized.errors)
        serialized.save()
        return Response(status=HTTP_200_OK)


class ScoreboardAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serialized = ScoreboardSerializer(PlayerWorkshop.objects.all(), many=True)
        return Response(serialized.data, status=HTTP_200_OK)


class TeamScoreAPIVIEW(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, player_workshop_id):
        try:
            score_transactions = ScoreTransaction.objects.filter(player_workshop_id=player_workshop_id)
        except ScoreTransaction.DoesNotExist:
            raise ScoreTransactionNotFound
        serialized = ScoreTransaction(score_transactions, many=True)
        return Response(serialized.data, status=HTTP_200_OK)
