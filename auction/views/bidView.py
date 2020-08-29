from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.shortcuts import render
from auction.serializers import *
from auction.models import *
from auction.views.permissions import *
from django.utils import timezone
def save_one_time_bid(request, auction, bid):
    try:
        participant = request.member.participant
        auction = OneTimeAuction.objects.filter(pk=auction)[0]
        bidder = OneTimeBidder.objects.filter(participant=participant, auction=auction)[0]
    except:
        return False
    if timezone.localtime() > auction.start_time:
        print("Salam")
    bidder.bid = bid
    bidder.save()
    if auction.winner.bid < bid:
        auction.winner = bidder
        auction.save()
    return True

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def new_one_time_bid(request):
    serializer = OneTimeBidSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    if save_one_time_bid(request, **data):
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
