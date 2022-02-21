import logging

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.serializers import PhoneNumberSerializer
from accounts.utils import find_user
from errors.error_codes import serialize_error
from fsm import permissions as customPermissions
from fsm.models import Team, Invitation, RegistrationReceipt, RegistrationForm, AnswerSheet
from fsm.permissions import IsInvitationInvitee
from fsm.serializers.answer_sheet_serializers import ReceiptGetSerializer, RegistrationReceiptSerializer
from fsm.serializers.team_serializer import TeamSerializer, InvitationSerializer, InvitationResponseSerializer

logger = logging.getLogger(__name__)


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['registration_form']
    my_tags = ['teams']

    serializer_action_classes = {
        'invite_member': InvitationSerializer
    }

    @property
    def paginator(self):
        self._paginator = super(TeamViewSet, self).paginator
        if self.action == 'list':
            self._paginator = None
        return self._paginator

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    def get_permissions(self):
        if self.action in ['create', 'make_team_head', 'register_and_join']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['get_invitations', 'retrieve']:
            permission_classes = [customPermissions.IsTeamMember]
        else:
            permission_classes = [customPermissions.IsTeamHead]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @action(detail=True, methods=['get'], permission_classes=[customPermissions.IsTeamMember])
    def get_invitations(self, request, pk=None):
        return Response(InvitationSerializer(Invitation.objects.filter(team=self.get_object(),
                                                                       status=Invitation.InvitationStatus.Waiting),
                                             many=True, context=self.get_serializer_context()).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[customPermissions.IsTeamHead])
    def invite_member(self, request, pk=None):
        team = self.get_object()
        serializer = InvitationSerializer(data=self.request.data,
                                          context={'team': team, **self.get_serializer_context()})
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['team'] = team
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=ReceiptGetSerializer, permission_classes=[IsAuthenticated])
    def make_team_head(self, request, pk=None):
        team = self.get_object()
        serializer = ReceiptGetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            receipt = serializer.validated_data['receipt']
            if receipt in team.members.all():
                team.team_head = receipt
                team.save()
            else:
                raise ParseError(serialize_error('4090'))
            return Response(TeamSerializer(context=self.get_serializer_context()).to_representation(team),
                            status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=PhoneNumberSerializer, permission_classes=[IsAuthenticated])
    def register_and_join(self, request, pk=None):  # todo: change name
        team = self.get_object()
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = find_user(serializer.validated_data)
            if len(RegistrationReceipt.objects.filter(answer_sheet_of=team.registration_form, user=user)) == 0:
                receipt = RegistrationReceipt.objects.create(
                    answer_sheet_of=team.registration_form,
                    user=user,
                    answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                    status=RegistrationReceipt.RegistrationStatus.Accepted,
                    is_participating=True,
                    team=team)
            else:
                receipt = RegistrationReceipt.objects.filter(
                    answer_sheet_of=team.registration_form, user=user).first()
                receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
                receipt.is_participating = True
                receipt.team = team
                receipt.save()

            return Response(TeamSerializer(context=self.get_serializer_context()).to_representation(team),
                            status=status.HTTP_200_OK)


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
        if invitation.status == Invitation.InvitationStatus.Accepted:
            raise ParseError(serialize_error('4056'))
        return super(InvitationViewSet, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[IsInvitationInvitee])
    def respond(self, request, pk=None):
        invitation = self.get_object()
        serializer = InvitationResponseSerializer(
            data=request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            invitee = invitation.invitee
            receipt = RegistrationReceipt.objects.filter(user=request.user, is_participating=True,
                                                         answer_sheet_of=invitation.team.registration_form).first()
            if receipt.team:
                raise PermissionDenied(serialize_error('4053'))
            invitation_status = serializer.validated_data.get(
                'status', Invitation.InvitationStatus.Waiting)
            team = invitation.team
            if invitation_status == Invitation.InvitationStatus.Accepted:
                if len(team.members.all()) >= team.registration_form.event_or_fsm.team_size:
                    raise ParseError('4059')
                invitation.status = Invitation.InvitationStatus.Accepted
                invitation.save()
                invitee.team = team
                invitee.save()
            return Response(
                data=InvitationSerializer(
                    context=self.get_serializer_context()).to_representation(invitation),
                status=status.HTTP_200_OK)
