from rest_framework import serializers
from apps.scoring.models import Cost


class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cost
        fields = ['value']
        read_only_fields = ['value']
