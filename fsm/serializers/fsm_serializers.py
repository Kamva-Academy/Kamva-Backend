from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from fsm.models import Event


class EventSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super(EventSerializer, self).create({'creator': self.context.get('user', None), **validated_data})

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator']
