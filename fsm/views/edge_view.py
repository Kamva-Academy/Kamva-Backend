import logging
import time

import redis
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
from fsm.models import Edge, FSM, PlayerHistory, TeamLock
from fsm.permissions import IsEdgeModifier
from fsm.serializers.fsm_serializers import EdgeSerializer, KeySerializer, TeamGetSerializer
from fsm.serializers.player_serializer import PlayerSerializer, PlayerHistorySerializer
from fsm.views.functions import get_player, move_on_edge, get_a_player_from_team
from workshop_backend.settings.production import REDIS_PORT, REDIS_HOST


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
        player = get_player(user, fsm)
        if player is None:
            raise ParseError(serialize_error('4082'))
        # todo check back enable
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            try:
                team_lock = team.lock
            except:
                team_lock = TeamLock.objects.create(team=team)
            if team_lock.is_locked:
                raise ParseError(serialize_error('4084'))
            else:
                team_lock.is_locked = True
                team_lock.save()
            try:
                if player.current_state == edge.head:
                    departure_time = timezone.now()
                    for member in team.members.all():
                        p = member.players.filter(fsm=fsm).first()
                        if p:
                            move_on_edge(p, edge, departure_time, is_forward=False)
                        if player.id == p.id:
                            player = p

                    team_lock.is_locked = False
                    team_lock.save()
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)

                elif player.current_state == edge.tail:
                    team_lock.is_locked = False
                    team_lock.save()
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)
                else:
                    team_lock.is_locked = False
                    team_lock.save()
                    raise ParseError(serialize_error('4083'))
            except Exception as e:
                team_lock.is_locked = False
                team_lock.save()
                raise e



        else:
            return InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def go_forward(self, request, pk):
        key = self.request.data.get('key', None)
        edge = self.get_object()
        fsm = edge.tail.fsm
        user = request.user
        player = get_player(user, fsm)
        if player is None:
            raise ParseError(serialize_error('4082'))
        if edge.is_hidden:
            raise PermissionDenied(serialize_error('4087'))
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            try:
                team_lock = team.lock
            except:
                team_lock = TeamLock.objects.create(team=team)
            if team_lock.is_locked:
                raise ParseError(serialize_error('4084'))
            else:
                team_lock.is_locked = True
                team_lock.save()
            try:
                if player.current_state == edge.tail:
                    if edge.lock and len(edge.lock) > 0:
                        if not key:
                            team_lock.is_locked = False
                            team_lock.save()
                            raise PermissionDenied(serialize_error('4085'))
                        elif edge.lock != key:
                            team_lock.is_locked = False
                            team_lock.save()
                            raise PermissionDenied(serialize_error('4084'))

                    # todo - handle scoring things - not needed now

                    departure_time = timezone.now()
                    for member in team.members.all():
                        p = member.players.filter(fsm=fsm).first()
                        if p:
                            move_on_edge(p, edge, departure_time, is_forward=True)

                    team_lock.is_locked = False
                    team_lock.save()
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)
                elif player.current_state == edge.head:
                    team_lock.is_locked = False
                    team_lock.save()
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)
                else:
                    team_lock.is_locked = False
                    team_lock.save()
                    raise ParseError(serialize_error('4083'))
            except Exception as e:
                team_lock.is_locked = False
                team_lock.save()
                raise e
        else:
            return InternalServerError('Not implemented Yet😎')

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
                if player.current_state == edge.tail:
                    departure_time = timezone.now()
                    for member in team.members.all():
                        p = member.players.filter(fsm=fsm).first()
                        if p:
                            move_on_edge(p, edge, departure_time, is_forward=True)
                        if player.id == p.id:
                            player = p
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
    def mentor_move_backward(self, request, pk):
        serializer = TeamGetSerializer(data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            edge = self.get_object()
            fsm = edge.tail.fsm
            player = get_a_player_from_team(team, fsm)
            if fsm.fsm_p_type == FSM.FSMPType.Team:
                if player.current_state == edge.head:
                    departure_time = timezone.now()
                    for member in team.members.all():
                        p = member.players.filter(fsm=fsm).first()
                        if p:
                            move_on_edge(p, edge, departure_time, is_forward=False)
                        if player.id == p.id:
                            player = p
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)
                elif player.current_state == edge.tail:
                    return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                    status=status.HTTP_200_OK)
                else:
                    raise ParseError(serialize_error('4083'))
            else:
                raise InternalServerError('Not implemented Yet😎')
