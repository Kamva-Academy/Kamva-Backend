from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from accounts.serializers import MerchandiseSerializer
from errors.error_codes import serialize_error
from fsm.models import Event, RegistrationReceipt


class EventSerializer(serializers.ModelSerializer):
    merchandise = MerchandiseSerializer(required=False)

    def create(self, validated_data):
        merchandise = validated_data.pop('merchandise', None)

        creator = self.context.get('user', None)
        holder = validated_data.get('holder', None)
        if holder and creator not in holder.admins.all():
            raise ParseError(serialize_error('4031'))
        instance = super(EventSerializer, self).create({'creator': self.context.get('user', None), **validated_data})

        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name', 'unnamed_event')
        serializer = MerchandiseSerializer(data=merchandise)
        if serializer.is_valid(raise_exception=True):
            merchandise_instance = serializer.save()
            instance.merchandise = merchandise_instance
            instance.save()
        return instance

    def to_representation(self, instance):
        representation = super(EventSerializer, self).to_representation(instance)
        user = self.context.get('user', None)
        registration = RegistrationReceipt.objects.filter(user=user, answer_sheet_of=instance.registration_form).last()
        # todo - add purchase information too
        representation['user_registration_status'] = registration.status if registration else 'NotRegistered'
        representation['user_purchase_status'] = 'NotPurchased' if instance.merchandise else 'Free'
        representation['participants_size'] = len(instance.participants)
        return representation

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'is_approved', 'participants_size', 'user_registration_status',
                            'user_purchase_status', 'registration_form']
