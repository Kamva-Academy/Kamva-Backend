from rest_framework import serializers
from apps.websiteappearance.models import Banner


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = ['image', 'redirect_to']
        read_only_fields = ['image', 'redirect_to']
