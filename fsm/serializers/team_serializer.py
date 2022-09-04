from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied

from accounts.models import User
from errors.error_codes import serialize_error
from fsm.models import Team, Invitation, RegistrationReceipt
from fsm.serializers.answer_sheet_serializers import RegistrationInfoSerializer


class InvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.PrimaryKeyRelatedField(queryset=RegistrationReceipt.objects.all(), required=False)
    username = serializers.CharField(max_length=150, required=False, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', None)
        invitee = attrs.get('invitee', None)
        team = self.context.get('team', None)
        if team is None:
            raise ParseError(serialize_error('4064'))

        if invitee is None:
            if username is None:
                raise ParseError(serialize_error('4063'))
            else:
                invitee = RegistrationReceipt.objects.filter(answer_sheet_of=team.registration_form,
                                                             user__username__exact=username).first()
                if invitee is None:
                    raise ParseError(serialize_error('4065'))
                self.context['invitee'] = invitee

        if len(team.members.all()) >= team.registration_form.event_or_fsm.team_size:
            raise PermissionDenied(serialize_error('4059'))
        if invitee.answer_sheet_of != team.registration_form:
            raise ParseError(serialize_error('4052'))
        if not invitee.is_participating:
            raise PermissionDenied(serialize_error('4055'))
        if invitee.team:
            raise ParseError(serialize_error('4053'))
        # if len(Invitation.objects.filter(invitee=invitee, team=team)) > 0:
        #     raise ParseError(serialize_error('4054'))

        return attrs

    def create(self, validated_data):
        if 'username' in validated_data.keys():
            validated_data.pop('username')
            validated_data['invitee'] = self.context.get('invitee', None)
        return super(InvitationSerializer, self).create({'team': self.context.get('team', None), **validated_data})

    def to_representation(self, instance):
        representation = super(InvitationSerializer, self).to_representation(instance)
        representation['first_name'] = instance.invitee.user.first_name
        representation['last_name'] = instance.invitee.user.last_name
        representation['phone_number'] = instance.invitee.user.phone_number

        representation['head_first_name'] = instance.team.team_head.user.first_name
        representation['head_last_name'] = instance.team.team_head.user.last_name
        representation['head_phone_number'] = instance.team.team_head.user.phone_number

        representation['team_name'] = instance.team.name
        return representation

    class Meta:
        model = Invitation
        fields = ['id', 'invitee', 'team', 'username', 'status']
        read_only_fields = ['id', 'team', 'status']


class TeamSerializer(serializers.ModelSerializer):
    members = RegistrationInfoSerializer(many=True, read_only=True)

    # todo: talk with Erfan about commenting this
    # def validate(self, attrs):
    #     registration_form = attrs.get('registration_form', None)
    #     user = self.context.get('user', None)
    #     user_registration = registration_form.registration_receipts.filter(user=user).first()
    #     if user in registration_form.event_or_fsm.modifiers:
    #         return attrs
    #     if not user_registration or not user_registration.is_participating:
    #         raise PermissionDenied(serialize_error('4050'))
    #     if Invitation.objects.filter(invitee=user_registration, team__registration_form=registration_form,
    #                                  status=Invitation.InvitationStatus.Accepted):
    #         raise PermissionDenied(serialize_error('4051'))
    #     return attrs

    def to_representation(self, instance):
        representation = super(TeamSerializer, self).to_representation(instance)
        return representation

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['id', 'team_head', 'members']


class InvitationResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Invitation.InvitationStatus.choices, required=True)
