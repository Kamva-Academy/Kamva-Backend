from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied

from errors.error_codes import serialize_error
from fsm.models import Team, Invitation, RegistrationReceipt
from fsm.serializers.answer_sheet_serializers import RegistrationInfoSerializer


class InvitationSerializer(serializers.ModelSerializer):
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), required=False)

    def validate(self, attrs):
        invitee = attrs.get('invitee', None)
        team = attrs.get('team', None)
        if len(team.members.all()) >= team.registration_form.event_or_fsm.team_size:
            raise PermissionDenied(serialize_error('4059'))
        if invitee.answer_sheet_of != team.registration_form:
            raise ParseError(serialize_error('4052'))
        if not invitee.is_participating:
            raise PermissionDenied(serialize_error('4055'))
        if invitee.team:
            raise ParseError(serialize_error('4053'))
        if len(Invitation.objects.filter(invitee=invitee, team=team)) > 0:
            raise ParseError(serialize_error('4054'))

        return attrs

    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ['id', 'has_accepted']


class TeamSerializer(serializers.ModelSerializer):
    members = RegistrationInfoSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        team = super(TeamSerializer, self).create(validated_data)
        user = self.context.get('user', None)
        user_registration = team.registration_form.registration_receipts.filter(user=user).first()
        invitation_serializer = InvitationSerializer(data={'team': team.id, 'invitee': user_registration.id})

        if invitation_serializer.is_valid(raise_exception=True):
            invitation_serializer.validated_data['has_accepted'] = True
            invitation_serializer.save()
        user_registration.team = team
        user_registration.save()
        team.team_head = user_registration
        team.save()
        return team

    def validate(self, attrs):
        registration_form = attrs.get('registration_form', None)
        user = self.context.get('user', None)
        user_registration = registration_form.registration_receipts.filter(user=user).first()
        if not user_registration or not user_registration.is_participating:
            raise PermissionDenied(serialize_error('4050'))
        if Invitation.objects.filter(invitee=user_registration, team__registration_form=registration_form,
                                     has_accepted=True):
            raise PermissionDenied(serialize_error('4051'))
        return attrs

    def to_representation(self, instance):
        representation = super(TeamSerializer, self).to_representation(instance)
        return representation

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['id', 'team_head', 'members']


class InvitationResponseSerializer(serializers.Serializer):
    has_accepted = serializers.BooleanField(required=True)
