from rest_framework import serializers
from apps.scoring.models import ScoreType


class ScoreTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScoreType
        fields = ['id', 'name']
