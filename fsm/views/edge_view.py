import logging

from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from fsm.models import Edge, FSM
from fsm.permissions import IsEdgeModifier
from fsm.serializers.fsm_serializers import EdgeSerializer, KeySerializer, TeamGetSerializer
from fsm.serializers.player_serializer import PlayerSerializer
from fsm.views.functions import get_player, move_on_edge, get_a_player_from_team

logger = logging.getLogger(__name__)


class EdgeViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    my_tags = ['edge']

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
        if self.action in ['create', 'retrieve', 'list', 'go_forward', 'go_backward']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsEdgeModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def go_backward(self, request, pk):
        edge = self.get_object()
        fsm = edge.tail.fsm
        user = request.user
        receipt = get_receipt(user, fsm)
        player = get_player(user, receipt)
        if player is None:
            raise ParseError(serialize_error('4082'))
        # todo check back enable
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            if player.receipt.id != team.team_head.id:
                raise ParseError(serialize_error('4089'))

            if player.current_state == edge.head:
                departure_time = timezone.now()
                for member in team.members.all():
                    p = member.players.filter(fsm=fsm).first()
                    if p:
                        p = move_on_edge(p, edge, departure_time, is_forward=False)
                        if player.id == p.id:
                            player = p
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            elif player.current_state == edge.tail:
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            else:
                raise ParseError(serialize_error('4083'))
        elif fsm.fsm_p_type in [FSM.FSMPType.Individual, FSM.FSMPType.Hybrid]:
            if player.current_state == edge.head:
                departure_time = timezone.now()
                player = move_on_edge(player, edge, departure_time, is_forward=False)
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            elif player.current_state == edge.tail:
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            else:
                raise ParseError(serialize_error('4083'))
        else:
            raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def go_forward(self, request, pk):
        key = self.request.data.get('key', None)
        edge = self.get_object()
        fsm = edge.tail.fsm
        user = request.user
        receipt = get_receipt(user, fsm)
        player = get_player(user, receipt)
        if player is None:
            raise ParseError(serialize_error('4082'))
        if not edge.is_visible:
            raise PermissionDenied(serialize_error('4087'))
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            if player.receipt.id != team.team_head.id:
                raise ParseError(serialize_error('4089'))

            if player.current_state == edge.tail:
                if edge.lock and len(edge.lock) > 0:
                    if not key:
                        raise PermissionDenied(serialize_error('4085'))
                    elif edge.lock != key:
                        raise PermissionDenied(serialize_error('4084'))

                # todo - handle scoring things

                departure_time = timezone.now()
                for member in team.members.all():
                    p = member.players.filter(fsm=fsm).first()
                    if p:
                        p = move_on_edge(p, edge, departure_time, is_forward=True)
                        if player.id == p.id:
                            player = p

                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            elif player.current_state == edge.head:
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            else:

                logger.warning(serialize_error('4083'))
                raise ParseError(serialize_error('4083'))
        elif fsm.fsm_p_type in [FSM.FSMPType.Individual, FSM.FSMPType.Hybrid]:
            if player.current_state == edge.tail:
                departure_time = timezone.now()
                player = move_on_edge(player, edge, departure_time, is_forward=True)
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            elif player.current_state == edge.head:
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            else:
                raise ParseError(serialize_error('4083'))
        else:
            raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def mentor_move_forward(self, request, pk):
        serializer = TeamGetSerializer(data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            edge = self.get_object()
            fsm = edge.tail.fsm
            player = get_a_player_from_team(team, fsm)

            if fsm.fsm_p_type == FSM.FSMPType.Team:

                departure_time = timezone.now()
                for member in team.members.all():
                    p = member.players.filter(fsm=fsm).first()
                    if p:
                        p = move_on_edge(p, edge, departure_time, is_forward=True)
                        if player.id == p.id:
                            player = p
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            else:
                raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def mentor_move_backward(self, request, pk):
        serializer = TeamGetSerializer(data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            edge = self.get_object()
            fsm = edge.tail.fsm
            player = get_a_player_from_team(team, fsm)

            if fsm.fsm_p_type == FSM.FSMPType.Team:

                departure_time = timezone.now()
                for member in team.members.all():
                    p = member.players.filter(fsm=fsm).first()
                    if p:
                        p = move_on_edge(p, edge, departure_time, is_forward=False)
                        if player.id == p.id:
                            player = p
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)

            else:
                raise InternalServerError('Not implemented Yet😎')
