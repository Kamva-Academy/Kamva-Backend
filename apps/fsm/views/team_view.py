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

from apps.accounts.serializers import PhoneNumberSerializer
from apps.accounts.utils import find_user
from errors.error_codes import serialize_error
from apps.fsm import permissions as customPermissions
from apps.fsm.models import Team, Invitation, RegistrationReceipt, AnswerSheet
from apps.fsm.permissions import IsInvitationInvitee
from apps.fsm.serializers.answer_sheet_serializers import ReceiptGetSerializer
from apps.fsm.serializers.team_serializer import TeamSerializer, InvitationSerializer, InvitationResponseSerializer
from apps.fsm.filtersets import TeamFilterSet

logger = logging.getLogger(__name__)


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TeamFilterSet
    my_tags = ['teams']
    pagination_class = None

    serializer_action_classes = {
        'invite_member': InvitationSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
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
            permission_classes = [customPermissions.IsTeamModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @action(detail=True, methods=['get'], permission_classes=[customPermissions.IsTeamMember])
    def get_team_invitations(self, request, pk=None):
        return Response(InvitationSerializer(Invitation.objects.filter(team=self.get_object()),
                                             many=True, context=self.get_serializer_context()).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: InvitationSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[customPermissions.IsTeamHead])
    def invite_member(self, request, pk=None):
        team = self.get_object()
        if len(Invitation.objects.filter(team=team,
                                         status=Invitation.InvitationStatus.Waiting,
                                         invitee__user__username=request.data.get('username'))) > 0:
            raise ParseError(serialize_error('4110'))

        serializer = InvitationSerializer(data=self.request.data,
                                          context={'team': team, **self.get_serializer_context()})

        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['team'] = team
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @swagger_auto_schema(responses={200: TeamSerializer()})
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_team_and_join(self, request):
        team_serializer = TeamSerializer(
            data=request.data, context={"user": request.user})
        team_serializer.is_valid(raise_exception=True)
        team = team_serializer.save()

        user_registration_receipt = team.registration_form.registration_receipts.filter(
            user=request.user).first()

        invitation_serializer = InvitationSerializer(
            data={'invitee': user_registration_receipt.id},
            context={'team': team})

        if invitation_serializer.is_valid(raise_exception=True):
            invitation_serializer.validated_data['status'] = Invitation.InvitationStatus.Accepted
            invitation_serializer.save()
        user_registration_receipt.team = team
        user_registration_receipt.save()
        team.team_head = user_registration_receipt
        team.save()

        return Response(team_serializer.data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'], serializer_class=ReceiptGetSerializer, permission_classes=[IsAuthenticated])
    def remove_from_team(self, request, pk=None):
        serializer = ReceiptGetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            receipt = serializer.validated_data['receipt']
            receipt.team = None
            receipt.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=PhoneNumberSerializer, permission_classes=[IsAuthenticated])
    def register_and_join(self, request, pk=None):  # todo: change name
        team = self.get_object()
        user = find_user(request.data)
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
            if hasattr(receipt, 'headed_team'):
                previous_team = getattr(receipt, 'headed_team')
                previous_team.team_head = None
                previous_team.save()
                receipt.headed_team = None
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
        except (KeyError, AttributeError):
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
            elif invitation_status == Invitation.InvitationStatus.Rejected:
                invitation.status = Invitation.InvitationStatus.Rejected
                invitation.save()
            return Response(
                data=InvitationSerializer(
                    context=self.get_serializer_context()).to_representation(invitation),
                status=status.HTTP_200_OK)
