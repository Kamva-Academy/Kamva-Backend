from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from fsm.views import permissions as custom_permissions
from .serializers import ScoreSerializer, ScoreboardSerializer, ScoreTransaction, ScoreTransactionsSerializer
from .exception import BadRequest, ScoreTransactionNotFound, PlayerWorkshopNotFound
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


#
#
# class TeamScoreAPIVIEW(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get(self, request, player_workshop_id):
#         try:
#             score_transactions = ScoreTransaction.objects.filter(player_workshop_id=player_workshop_id)
#         except ScoreTransaction.DoesNotExist:
#             raise ScoreTransactionNotFound
#
#         return Response({''}, status=HTTP_200_OK)


class PlayerScoreHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if 'player_workshop_id' not in request.data.keys():
            return Response({'success': False, 'error': "اطلاعات مربوط به عضویت در کارگاه موجود نیست."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                player_workshop = PlayerWorkshop.objects.get(id=request.data['player_workshop_id'])
            except PlayerWorkshop.DoesNotExist:
                raise PlayerWorkshopNotFound
        score_transactions = ScoreTransaction.objects.filter(player_workshop=player_workshop)
        serialized = ScoreTransactionsSerializer(score_transactions, many=True)
        return Response(serialized.data, status=HTTP_200_OK)


class PlayerCurrentScoreAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if 'player_workshop_id' not in request.data.keys():
            return Response({'success': False, 'error': "اطلاعات مربوط به عضویت در کارگاه موجود نیست."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                player_workshop = PlayerWorkshop.objects.get(id=request.data['player_workshop_id'])
            except PlayerWorkshop.DoesNotExist:
                raise PlayerWorkshopNotFound
        score_transactions = ScoreTransaction.objects.filter(player_workshop=player_workshop).aggregate(Sum('score'))
        return Response({'success': True, 'score': score_transactions})


@transaction.atomic
def submit_score(player_workshop, score, description):
    if len(ScoreTransaction.objects.filter(description=description, player_workshop=player_workshop, score=score)) <= 0:
        ScoreTransaction.objects.create(player_workshop=player_workshop, score=score, description=description)


def get_score(player_workshop, ):
    pass


def get_player_workshop(player, fsm):
    PlayerWorkshop.objects.get(player=player, workshop=fsm)
