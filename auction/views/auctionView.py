import pytz
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
@permission_classes([permissions.IsAuthenticated])
@transaction.atomic
def new_one_time_auction(request):
    data = request.data
    participant = request.user.participant
    team = participant.team
    values = data['values']
    auction = OneTimeAuction.objects.create(auction_pay_type= data['auction_pay_type'])
    participants = team.participant_set.all()
    index = 0
    while index < len(values):
        OneTimeBidder.objects.create(
            auction=auction,
            participant=participants[index],
            value=values[index] if index < len(values) else 50
        )
        index += 1
    participant = request.user.participant
    bider = OneTimeBidder.objects.filter(participant=participant, auction=auction)
    remained_time = (auction.end_time() - datetime.now(auction.end_time().tzinfo)).seconds
    if  auction.end_time() < datetime.now(auction.start_time.tzinfo):
        remained_time = -10000
    response = {
        "auction":
            {
                "id": auction.id,
                "auction_pay_type": auction.auction_pay_type,
                "start_time": str(auction.start_time),
                "end_time": str(auction.end_time()),
                "winner": auction.winner_id,
                "remained_time": remained_time,

            }
    }
    if bider.count()>0:
        bider = bider[0]
        response["my_value"] = bider.value
    return Response(response)


class LastAuction(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        participant = request.user.participant
        biders = OneTimeBidder.objects.filter(participant=participant).order_by("-auction__id")
        last_auction = biders[0].auction
        my_bidder = OneTimeBidder.objects.filter(participant=participant, auction=last_auction)
        remained_time = (last_auction.end_time() - datetime.now(last_auction.end_time().tzinfo)).seconds

        if last_auction.end_time() < datetime.now(last_auction.end_time().tzinfo):
            remained_time = -10000
        response = {
            "my_value": my_bidder[0].value,
            "auction":
                {
                    "id": last_auction.id,
                    "auction_pay_type": last_auction.auction_pay_type,
                    "start_time": str(last_auction.start_time),
                    "end_time": str(last_auction.end_time()),
                    "current_time": str(datetime.now(last_auction.end_time().tzinfo)),
                    "winner": last_auction.winner_id,
                    "remained_time":remained_time
                }
        }

        return Response(response)


class AuctionResult(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        participant = request.user.participant
        biders = OneTimeBidder.objects.filter(participant=participant).order_by("-auction__id")
        last_auction = biders[0].auction
        my_bidder = OneTimeBidder.objects.filter(participant=participant, auction=last_auction)
        all_bidders = OneTimeBidder.objects.filter(auction=last_auction)

        remained_time = (last_auction.end_time() - datetime.now(last_auction.end_time().tzinfo)).seconds
        if last_auction.end_time() < datetime.now(last_auction.end_time().tzinfo):
            remained_time = -10000
        response = {
            "my_value": my_bidder[0].value,
            "auction":
                {
                    "id": last_auction.id,
                    "auction_pay_type": last_auction.auction_pay_type,
                    "start_time": str(last_auction.start_time),
                    "end_time": str(last_auction.end_time()),
                    "winner": last_auction.winner_id,
                    "remained_time":remained_time

                },
            "bidders": []
        }
        if last_auction.winner:
            response['winner_value'] = last_auction.winner.value
        for bid in all_bidders:
            response['bidders'].append(
                {
                    'value':bid.value,
                    'bid': bid.bid
                }
            )
        return Response(response)
