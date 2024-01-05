from rest_framework import serializers
from apps.scoring.models import Reward


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['value']
        read_only_fields = ['value']
