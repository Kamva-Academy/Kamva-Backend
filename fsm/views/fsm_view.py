from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ParseError, NotFound
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from accounts.serializers import AccountSerializer
from accounts.utils import find_user
from errors.error_codes import serialize_error
from fsm.models import FSM, State, PlayerHistory, Player, Edge, logging
from fsm.permissions import MentorPermission, HasActiveRegistration, PlayerViewerPermission
from fsm.serializers.fsm_serializers import FSMSerializer, FSMGetSerializer, KeySerializer, EdgeSerializer, \
    TeamGetSerializer
from fsm.serializers.paper_serializers import StateSerializer, StateSimpleSerializer, EdgeSimpleSerializer
from fsm.serializers.player_serializer import PlayerSerializer, PlayerHistorySerializer
from fsm.views.functions import get_player, get_receipt, get_a_player_from_team

logger = logging.getLogger(__name__)

class FSMViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FSM.objects.all()
    serializer_class = FSMSerializer
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'add_mentor', 'get_states', 'get_edges','get_player_from_team']:
            permission_classes = [MentorPermission]
        elif self.action in ['enter', 'get_self']:
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def enter(self, request, pk=None):
        key = self.request.data.get('key', None)
        fsm = self.get_object()
        user = self.request.user
        # TODO - add for hybrid and individual
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            receipt = get_receipt(user, fsm)
            player = get_player(user, fsm)
            if receipt is None:
                raise ParseError('4079')
            if receipt.team is None:
                raise ParseError(serialize_error('4078'))

            # first time entering fsm
            if not player:
                if fsm.lock and len(fsm.lock) > 0:
                    if not key:
                        raise PermissionDenied(serialize_error('4085'))
                    elif key != fsm.lock:
                        raise PermissionDenied(serialize_error('4080'))
                serializer = PlayerSerializer(data={'user': user.id, 'fsm': fsm.id, 'receipt': receipt.id,
                                                    'current_state': fsm.first_state.id, 'last_visit': timezone.now()},
                                              context=self.get_serializer_context())
                if serializer.is_valid(raise_exception=True):
                    player = serializer.save()
                serializer = PlayerHistorySerializer(data={'player': player.id, 'state': player.current_state.id,
                                                           'start_time': player.last_visit},
                                                     context=self.get_serializer_context())
                if serializer.is_valid(raise_exception=True):
                    player_history = serializer.save()
            else:
                player_history = PlayerHistory.objects.filter(player=player, state=player.current_state).last()
                if player_history is None:
                    raise NotFound(serialize_error('4081'))
            return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                            status=status.HTTP_200_OK)
        return Response('not implemented yet')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def get_self(self, request, pk=None):
        fsm = self.get_object()
        user = self.request.user
        player = get_player(user, fsm)
        if player:
            return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                            status=status.HTTP_200_OK)
        else:
            raise NotFound(serialize_error('4081'))

    @swagger_auto_schema(responses={200: StateSimpleSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def get_states(self, request, pk):
        return Response(data=StateSimpleSerializer(self.get_object().states, context=self.get_serializer_context(),
                                                   many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: EdgeSimpleSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def get_edges(self, request, pk):
        edges = Edge.objects.filter(Q(tail__fsm=self.get_object()) | Q(head__fsm=self.get_object()))
        return Response(data=EdgeSerializer(edges, context=self.get_serializer_context(), many=True).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: FSMSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AccountSerializer, permission_classes=[MentorPermission, ])
    def add_mentor(self, request, pk=None):
        data = request.data
        fsm = self.get_object()
        serializer = AccountSerializer(data=data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            new_mentor = find_user(serializer.validated_data)
            fsm.mentors.add(new_mentor)
            return Response(FSMSerializer(context=self.get_serializer_context()).to_representation(fsm),
                            status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def get_player_from_team(self, request, pk):
        fsm = self.get_object()
        serializer = TeamGetSerializer(data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            player = get_a_player_from_team(team, fsm)
            return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                                status=status.HTTP_200_OK)


class PlayerViewSet(viewsets.GenericViewSet, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action in ['retrieve']:
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
