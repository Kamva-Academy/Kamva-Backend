from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from apps.fsm.models import FSM, Player
from apps.fsm.permissions import PlayerViewerPermission
from apps.fsm.models import FSM
from apps.fsm.serializers.fsm_serializers import KeySerializer, TeamGetSerializer
from apps.fsm.serializers.player_serializer import PlayerSerializer
from apps.fsm.views.functions import move_on_edge, get_player_latest_taken_edge


class PlayerViewSet(viewsets.GenericViewSet, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action in ['retrieve', 'mentor_move_backward']:
            permission_classes = [PlayerViewerPermission]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @swagger_auto_schema(tags=['mentor'])
    def retrieve(self, request, *args, **kwargs):
        return super(PlayerViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def go_backward(self, request, pk):
        player = self.get_object()
        fsm = player.fsm
        edge = get_player_latest_taken_edge(player)

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
                        p = move_on_edge(
                            p, edge, departure_time, is_forward=False)
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
                player = move_on_edge(
                    player, edge, departure_time, is_forward=False)
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)
            elif player.current_state == edge.tail:
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
        serializer = TeamGetSerializer(
            data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            player = self.get_object()
            fsm = player.fsm
            edge = get_player_latest_taken_edge(player)

            if fsm.fsm_p_type == FSM.FSMPType.Team:

                departure_time = timezone.now()
                for member in team.members.all():
                    p = member.players.filter(fsm=fsm).first()
                    if p:
                        p = move_on_edge(
                            p, edge, departure_time, is_forward=False)
                        if player.id == p.id:
                            player = p
                return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)

            else:
                raise InternalServerError('Not implemented Yet😎')
