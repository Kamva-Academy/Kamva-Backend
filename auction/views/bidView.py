from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.shortcuts import render
from auction.serializers import *
from auction.models import *
from auction.views.permisions import *
def newBid(request, bid):
    try:
        member = Member.object.filter(user_pk = request.user.pk)[0]
    except:
        pass

    bidder = OneTimeBidder.object.filter(member=member)[0] 
    bidder.bid = bid
    bidder.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def one_time_bid(request):
    serializer = OneTimeBidderSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    newBid(request, **data)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def british_bid(request):
    pass
