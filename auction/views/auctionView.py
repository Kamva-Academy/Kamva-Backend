from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from django.shortcuts import render
from auction.serializers import *
from auction.models import *
from auction.views.permissions import *
from django.utils import timezone

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@transaction.atomic
def new_one_time_auction(request):
    serializer = OneTimeAuctionPostSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    instance = serializer.create(data)

    participant = request.user.participant
    biders = OneTimeBidder.objects.filter(participant=participant).order_by("-auction__start_time")
    last_auction = biders[0].auction
    my_bidder = OneTimeBidder.objects.filter(participant=participant, auction=last_auction)
    response = {
        "my_value": my_bidder[0].value,
        "auction":
            {
                "id": last_auction.id,
                "auction_pay_type": last_auction.auction_pay_type,
                "start_time": str(last_auction.start_time),
                "end_time": str(last_auction.end_time),
                "winner": last_auction.winner_id
            }
    }

    if instance is not None:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OneTimeAuctionView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin):
    #permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]
    permission_classes = [permissions.AllowAny]

    queryset = OneTimeAuction.objects.all()
    serializer_class = OneTimeAuctionSerializer


class LastAuction(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        participant = request.user.participant
        biders = OneTimeBidder.objects.filter(participant=participant).order_by("-auction__start_time")
        last_auction = biders[0].auction
        my_bidder = OneTimeBidder.objects.filter(participant=participant, auction=last_auction)
        response = {
            "my_value": my_bidder[0].value,
            "auction":
                {
                    "id": last_auction.id,
                    "auction_pay_type": last_auction.auction_pay_type,
                    "start_time": str(last_auction.start_time),
                    "end_time": str(last_auction.end_time),
                    "winner": last_auction.winner_id
                }
        }

        return Response(response)

