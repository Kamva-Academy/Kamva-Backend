from rest_framework import serializers

from fsm.serializers.serializers import PlayerWorkshopSerializer
from .models import ScoreTransaction
from django.db import transaction
from fsm.models import PlayerWorkshop
from .exception import PlayerWorkshopNotFound


class ScoreSerializer(serializers.ModelSerializer):
    player_workshop_id = serializers.StringRelatedField()

    class Meta:
        model = ScoreTransaction
        fields = ('id', 'score', 'description', 'player_workshop_id')

    @transaction.atomic
    def create(self, validated_data):
        player_workshop_id = validated_data.pop('player_workshop_id')
        score = validated_data.pop('score')
        description = validated_data.pop('description')
        try:
            player_workshop = PlayerWorkshop.objects.get(id=player_workshop_id)
        except PlayerWorkshop.DoesNotExist:
            raise PlayerWorkshopNotFound
        return ScoreTransaction.objects.create(score, description, player_workshop)

    def update(self, instance, validated_data):
        player_workshop_id = validated_data.get('player_workshop_id', instance.player_workshop.id)
        try:
            player_workshop = PlayerWorkshop.objects.get(id=player_workshop_id)
        except PlayerWorkshop.DoesNotExist:
            raise PlayerWorkshopNotFound
        instance.player_workshop = player_workshop
        instance.score = validated_data.get('score', instance.score)
        instance.description = validated_data.pop('description', instance.description)
        instance.save()
        return instance


class ScoreboardSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    player_workshop = PlayerWorkshopSerializer()

    class Meta:
        model = ScoreTransaction
        fields = ['score', 'player_workshop']

    @staticmethod
    def get_score(obj):
        return ScoreTransaction.objects.get_team_total_score(obj)


class ScoreTransactionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScoreTransaction
        fields = '__all__'
