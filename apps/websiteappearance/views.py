from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from apps.fsm.models import *

from apps.websiteappearance.models import Banner
from apps.websiteappearance.serializers import BannerSerializer


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer

    @swagger_auto_schema(tags=['website appearance'])
    def list(self, request, *args, **kwargs):
        banner_type = request.query_params.get('banner_type')
        banners = self.queryset.filter(banner_type=banner_type)
        return Response(data=self.serializer_class(banners, many=True).data, status=status.HTTP_200_OK)
