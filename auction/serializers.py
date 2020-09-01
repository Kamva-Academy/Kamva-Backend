from rest_framework import serializers
from auction.models import *
from accounts.models import *

class OneTimeBidSerializer(serializers.Serializer):
    auction = serializers.IntegerField()
    bid = serializers.IntegerField()

class OneTimeAuctionPostSerializer(serializers.Serializer):
    values = serializers.ListField(child=serializers.IntegerField())
    team = serializers.IntegerField()
    auction_pay_type = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    
    def create(self, validated_data):
        values = validated_data.pop('values')
        team = validated_data.pop('team')
        try:
            team = Team.objects.filter(id=team)[0]
        except:
            return None
        print(validated_data)
        instance = OneTimeAuction.objects.create(**validated_data)
        participants = team.participant_set.all()
        index = 0
        while index < len(values):
            OneTimeBidder.objects.create(
                auction=instance,
                participant=participants[index],
                value=values[index] if index < len(values) else 50
                )
            index +=1
        return instance


class OneTimeBidderSerializer(serializers.ModelSerializer):
    class Meta():
        model = OneTimeBidder
        fields = '__all__'

class OneTimeAuctionSerializer(serializers.ModelSerializer):
    bidders = OneTimeBidderSerializer(many=True)
    class Meta():
        model = OneTimeAuction
        fields = '__all__'

