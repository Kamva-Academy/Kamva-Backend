from rest_framework import serializers

from fsm.models import Player, PlayerHistory


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']


class PlayerHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlayerHistory
        fields = '__all__'
        read_only_fields = ['id']
