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
def new_one_time_auction(request):
    serializer = OneTimeAuctionPostSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    instance = serializer.create(data)
    if instance is not None:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OneTimeAuctionView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin):
    #permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]
    permission_classes = [permissions.AllowAny]

    queryset = OneTimeAuction.objects.all()
    serializer_class = OneTimeAuctionSerializer
