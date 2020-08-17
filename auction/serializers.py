from rest_framework import serializers
from auction.models import *


class OneTimeBidderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneTimeBidder
        fields = ['bid']
