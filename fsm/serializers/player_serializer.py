from rest_framework import serializers

from fsm.models import Player, PlayerHistory
from fsm.serializers.paper_serializers import StateSerializer
from fsm.serializers.team_serializer import TeamSerializer


class PlayerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHistory
        fields = '__all__'
        read_only_fields = ['id']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super(PlayerSerializer, self).to_representation(instance)
        representation['current_state'] = StateSerializer(context=self.context).to_representation(
            instance.current_state)
        player_history = PlayerHistory.objects.filter(player=instance, state=instance.current_state).last()
        representation['latest_history'] = PlayerHistorySerializer(context=self.context).to_representation(
            player_history) if player_history else None
        representation['team'] = TeamSerializer(context=self.context).to_representation(
            instance.team) if instance.team else None
        representation['full_name'] = instance.user.full_name
        return representation
