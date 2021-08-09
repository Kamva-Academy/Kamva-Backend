from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from errors.error_codes import serialize_error
from fsm.models import Event


class EventSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        creator = self.context.get('user', None)
        holder = validated_data.get('holder', None)
        if holder and creator not in holder.admins.all():
            raise ParseError(serialize_error('4031'))
        return super(EventSerializer, self).create({'creator': self.context.get('user', None), **validated_data})

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator']
