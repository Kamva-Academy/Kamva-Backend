from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from accounts.serializers import MerchandiseSerializer, AccountSerializer
from errors.error_codes import serialize_error
from fsm.models import Event, RegistrationReceipt, FSM
from fsm.serializers.serializers import MainStateGetSerializer


class EventSerializer(serializers.ModelSerializer):
    merchandise = MerchandiseSerializer(required=False)

    def create(self, validated_data):
        merchandise = validated_data.pop('merchandise', None)

        creator = self.context.get('user', None)
        instance = super(EventSerializer, self).create({'creator': creator, **validated_data})

        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name', 'unnamed_event')
            serializer = MerchandiseSerializer(data=merchandise)
            if serializer.is_valid(raise_exception=True):
                merchandise_instance = serializer.save()
                instance.merchandise = merchandise_instance
                instance.save()
        return instance

    def validate(self, attrs):
        team_size = attrs.get('team_size', 0)
        event_type = attrs.get('event_type', Event.EventType.Individual)
        if (team_size > 0 and event_type != Event.EventType.Team) or (event_type == Event.EventType.Team and team_size <= 0):
            raise ParseError(serialize_error('4074'))
        creator = self.context.get('user', None)
        holder = attrs.get('holder', None)
        if holder and creator not in holder.admins.all():
            raise ParseError(serialize_error('4031'))
        return attrs

    def to_representation(self, instance):
        representation = super(EventSerializer, self).to_representation(instance)
        user = self.context.get('user', None)
        registration = RegistrationReceipt.objects.filter(user=user, answer_sheet_of=instance.registration_form).last()
        representation['user_registration_status'] = registration.status if registration else 'NotRegistered'
        representation['is_paid'] = registration.is_paid if registration else False
        representation['is_user_participating'] = registration.is_participating if registration else False
        representation['participants_size'] = len(instance.participants)
        representation['registration_receipt'] = registration.id if registration else None
        return representation

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'is_approved', 'participants_size', 'user_registration_status',
                            'is_paid', 'registration_form']


class FSMSerializer(serializers.ModelSerializer):
    lock = serializers.CharField(required=False, write_only=True)
    merchandise = MerchandiseSerializer(required=False)
    mentors = AccountSerializer(many=True, read_only=True)

    def validate(self, attrs):
        event = attrs.get('event', None)
        team_size = attrs.get('team_size', None)
        merchandise = attrs.get('merchandise', None)
        registration_form = attrs.get('registration_form', None)
        holder = attrs.get('registration_form', None)
        fsm_p_type = attrs.get('fsm_p_type', FSM.FSMPType.Individual)
        creator = self.context.get('user', None)
        if event:
            if merchandise or registration_form:
                raise ParseError(serialize_error('4069'))
            if holder != event.holder:
                raise ParseError(serialize_error('4070'))
            if fsm_p_type == FSM.FSMPType.Individual:
                if event.event_type != Event.EventType.Individual:
                    raise ParseError(serialize_error('4071'))
            else:
                if event.event_type == Event.EventType.Individual:
                    raise ParseError(serialize_error('4071'))
                if team_size and team_size != event.team_size:
                    raise ParseError(serialize_error('4072'))
            if creator not in event.modifiers:
                raise ParseError(serialize_error('4073'))
        else:
            if holder and creator not in holder.admins.all():
                raise ParseError(serialize_error('4031'))
            if fsm_p_type == FSM.FSMPType.Team and team_size is None:
                raise ParseError(serialize_error('4074'))
        return attrs

    def create(self, validated_data):
        creator = self.context.get('user', None)
        merchandise = validated_data.pop('merchandise', None)
        team_size = validated_data.get('team_size', None)
        event = validated_data.get('event', None)
        fsm_p_type = validated_data.get('fsm_p_type')
        if team_size is None and event and fsm_p_type != FSM.FSMPType.Individual:
            validated_data['team_size'] = event.team_size

        instance = super(FSMSerializer, self).create({'creator': creator, **validated_data})

        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name', 'unnamed_event')
            serializer = MerchandiseSerializer(data=merchandise)
            if serializer.is_valid(raise_exception=True):
                merchandise_instance = serializer.save()
                instance.merchandise = merchandise_instance
                instance.save()
        return instance

    class Meta:
        model = FSM
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'mentors', 'first_state', 'registration_form']



class FSMRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = '__all__'


class CreateFSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = ['name', 'type', 'active', ]


class FSMGetSerializer(serializers.ModelSerializer):
    states = MainStateGetSerializer(many=True)

    class Meta:
        model = FSM
        fields = '__all__'
