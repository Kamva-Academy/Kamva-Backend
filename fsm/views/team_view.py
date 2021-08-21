import logging

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.response import Response

from accounts.models import Teamm
from accounts.serializers import TeammSerializer
from errors.error_codes import serialize_error
from fsm import permissions as customPermissions
from fsm.models import Team, Invitation, RegistrationReceipt, RegistrationForm
from fsm.permissions import IsInvitationInvitee
from fsm.serializers.team_serializer import TeamSerializer, InvitationSerializer, InvitationResponseSerializer

logger = logging.getLogger(__name__)


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    my_tags = ['teams']

    serializer_action_classes = {
        'invite_member': InvitationSerializer,
        'revoke_invitation': InvitationSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'get_pending_invitations':
            permission_classes = [customPermissions.IsTeamMember]
        else:
            permission_classes = [customPermissions.IsTeamHead]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @action(detail=True, methods=['get'], permission_classes=[customPermissions.IsTeamMember])
    def get_invitations(self, request, pk=None):
        return Response(InvitationSerializer(Invitation.objects.filter(team=self.get_object(), has_accepted=False),
                                             many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[customPermissions.IsTeamHead])
    def invite_member(self, request, pk=None):
        team = self.get_object()
        serializer = InvitationSerializer(data=self.request.data, context={'team': team})
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['team'] = team
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class InvitationViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.ListModelMixin):
    queryset = Invitation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer
    my_tags = ['teams']

    serializer_action_classes = {
        'respond': InvitationResponseSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        invitation = self.get_object()
        if invitation.team.team_head.user != request.user:
            raise PermissionDenied(serialize_error('4060'))
        if invitation.has_accepted:
            raise ParseError(serialize_error('4056'))
        return super(InvitationViewSet, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[IsInvitationInvitee])
    def respond(self, request, pk=None):
        invitation = self.get_object()
        serializer = InvitationResponseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            invitee = invitation.invitee
            receipt = RegistrationReceipt.objects.filter(user=request.user, is_participating=True,
                                                         answer_sheet_of=invitation.team.registration_form).first()
            if receipt.team:
                raise PermissionDenied(serialize_error('4053'))
            has_accepted = serializer.validated_data.get('has_accepted', False)
            team = invitation.team
            if has_accepted:
                if len(team.members.all()) >= team.registration_form.event_or_fsm.team_size:
                    raise ParseError('4059')
                invitation.has_accepted = has_accepted
                invitation.save()
                invitee.team = team
                invitee.save()
            return Response(data=InvitationSerializer().to_representation(invitation), status=status.HTTP_200_OK)
