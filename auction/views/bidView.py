from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.shortcuts import render
from auction.serializers import *
from auction.models import *
from auction.views.permissions import *
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

@transaction.atomic
@permission_classes([permissions.AllowAny])
def save_one_time_bid(request, auction, bid):
    try:
        participant = request.user.participant
        auction = OneTimeAuction.objects.filter(pk=auction)[0]
        bidder = OneTimeBidder.objects.filter(participant=participant, auction=auction)[0]
    except:
        return {"success": False, "message":"bad request"}

    if timezone.localtime() > auction.start_time:
        logger.debug(f'timezone.localtime() > auction.start_time is True')
    bidder.bid = bid
    bidder.save()
    if auction.start_time < datetime.now() + timedelta(days=1) < auction.end_time:
        if(not auction.winner or  auction.winner.bid < bid):
            auction.winner = bidder
            auction.save()
        response = {
            "value": bidder.value,
            "bid": bidder.bid
        }
        return response
    return {"success": False, "message":"زمان مزایده به پایان رسیده",
            "end_time": auction.end_time,
            "local_time": datetime.now(),
            "auction": auction.id}


@api_view(['POST'])
@transaction.atomic
@permission_classes([permissions.AllowAny])
def new_one_time_bid(request):
    serializer = OneTimeBidSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    return Response(save_one_time_bid(request, **data))
