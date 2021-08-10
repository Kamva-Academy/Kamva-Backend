from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from errors.error_codes import serialize_error
from fsm.models import Event, RegistrationReceipt


class EventSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        creator = self.context.get('user', None)
        holder = validated_data.get('holder', None)
        if holder and creator not in holder.admins.all():
            raise ParseError(serialize_error('4031'))
        return super(EventSerializer, self).create({'creator': self.context.get('user', None), **validated_data})

    def to_representation(self, instance):
        representation = super(EventSerializer, self).to_representation(instance)
        user = self.context.get('user', None)
        registration = RegistrationReceipt.objects.filter(user=user, answer_sheet_of=instance.registration_form).last()
        # todo - add purchase information too
        representation['user_registration_status'] = registration.status if registration else 'NotRegistered'
        representation['user_purchase_status'] = 'NotPurchased'
        return representation

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'user_registration_status', 'user_purchase_status']
