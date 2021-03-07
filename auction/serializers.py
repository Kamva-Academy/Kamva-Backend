# from rest_framework import serializers
# from auction.models import *
# from accounts.models import *
#
# import logging
# logger = logging.getLogger(__name__)
#
# class OneTimeBidSerializer(serializers.Serializer):
#     auction = serializers.IntegerField()
#     bid = serializers.IntegerField()
#
# class OneTimeBidderSerializer(serializers.ModelSerializer):
#     class Meta():
#         model = OneTimeBidder
#         fields = '__all__'
#
# class OneTimeAuctionSerializer(serializers.ModelSerializer):
#     bidders = OneTimeBidderSerializer(many=True)
#     class Meta():
#         model = OneTimeAuction
#         fields = '__all__'
#
