from rest_framework import serializers
from auction.models import *
from accounts.models import *

class OneTimeBidSerializer(serializers.Serializer):
    auction = serializers.IntegerField()
    bid = serializers.IntegerField()

class OneTimeAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneTimeAuction
        fields = '__all__'
    
    def create(self, validated_data):
        instance = OneTimeAuction.objects.create(**validated_data)
        for ability_data in abilities_data:
            ability = Ability.objects.create(**ability_data)
            ability.edge = instance
            ability.save()
    
        return instance

