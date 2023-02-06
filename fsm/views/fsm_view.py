from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ParseError, NotFound
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from accounts.serializers import AccountSerializer
from accounts.utils import find_user
from errors.error_codes import serialize_error
from fsm.filtersets import FSMFilterSet
from fsm.models import AnswerSheet, RegistrationReceipt, FSM, State, PlayerHistory, Player, Edge, logging, RegistrationReceipt, Problem
from fsm.permissions import MentorPermission, HasActiveRegistration, PlayerViewerPermission
from fsm.serializers.fsm_serializers import FSMSerializer, KeySerializer, EdgeSerializer, \
    TeamGetSerializer
from fsm.serializers.paper_serializers import StateSerializer, StateSimpleSerializer, EdgeSimpleSerializer
from fsm.serializers.player_serializer import PlayerSerializer, PlayerHistorySerializer
from fsm.serializers.widget_serializers import MockWidgetSerializer
from fsm.serializers.widget_polymorphic import WidgetPolymorphicSerializer
from fsm.views.functions import get_player, get_receipt, get_a_player_from_team

logger = logging.getLogger(__name__)


class FSMViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FSM.objects.all()
    serializer_class = FSMSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = FSMFilterSet
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action in ['partial_update', 'update', 'destroy', 'add_mentor', 'get_states', 'get_edges',
                           'get_player_from_team', 'activate', 'players']:
            permission_classes = [MentorPermission]
        elif self.action in ['enter', 'get_self', 'review']:
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['players']:
            return PlayerSerializer
        else:
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
        logger.info(f'user {user.full_name} trying to enter fsm {fsm.name}')
        receipt = get_receipt(user, fsm)
        player = get_player(user, fsm, receipt)

        if receipt is None:
            raise ParseError(serialize_error('4079'))
        # TODO - add for hybrid and individual
        if fsm.fsm_p_type in [FSM.FSMPType.Team, FSM.FSMPType.Hybrid]:
            if receipt.team is None:
                raise ParseError(serialize_error('4078'))

        if not fsm.first_state:
            raise ParseError(serialize_error('4111'))

        if not fsm.first_state.is_user_permitted(user):
            raise ParseError(serialize_error('4108'))

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
            # if any state has been deleted and player has no current state:
            if player.current_state is None:
                player.current_state = fsm.first_state
                player.save()

            player_history = PlayerHistory.objects.filter(
                player=player, state=player.current_state).last()
            if player_history is None:
                logger.info(
                    f'user {user.full_name} has player [id:{player.id}] without corresponding history')
            #     raise NotFound(serialize_error('4081'))
        return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                        status=status.HTTP_200_OK)

    # @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    # @transaction.atomic
    # @action(detail=True, methods=['get'])
    # def get_self(self, request, pk=None):
    #     fsm = self.get_object()
    #     user = self.request.user
    #     player = get_player(user, fsm)
    #     if player:
    #         return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
    #                         status=status.HTTP_200_OK)
    #     else:
    #         raise NotFound(serialize_error('4081'))

    @swagger_auto_schema(responses={200: MockWidgetSerializer}, tags=['player', 'fsm'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def review(self, request, pk):
        problems = Problem.objects.filter(
            paper__in=self.get_object().states.filter(is_exam=True))
        return Response(WidgetPolymorphicSerializer(problems, context=self.get_serializer_context(), many=True).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def players(self, request, pk):
        gender = request.query_params.get('gender', None)
        first_name = request.query_params.get('first_name', None)
        last_name = request.query_params.get('last_name', None)

        queryset = self.get_object().players.all()
        queryset = queryset.filter(
            user__gender=gender) if gender is not None else queryset
        queryset = queryset.filter(
            user__first_name__startswith=first_name) if first_name is not None else queryset
        queryset = queryset.filter(
            user__first_name__startswith=last_name) if last_name is not None else queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        edges = Edge.objects.filter(
            Q(tail__fsm=self.get_object()) | Q(head__fsm=self.get_object()))
        return Response(data=EdgeSerializer(edges, context=self.get_serializer_context(), many=True).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: AccountSerializer(many=True)}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def get_mentors(self, request, pk):
        mentors = self.get_object().mentors
        return Response(data=AccountSerializer(mentors, context=self.get_serializer_context(), many=True).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: FSMSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AccountSerializer, permission_classes=[MentorPermission, ])
    def add_mentor(self, request, pk=None):
        data = request.data
        fsm = self.get_object()
        account_serializer = AccountSerializer(
            data=data, context=self.get_serializer_context())
        if account_serializer.is_valid(raise_exception=True):
            new_mentor = find_user(account_serializer.validated_data)
            fsm.mentors.add(new_mentor)
            registration_form = fsm.event.registration_form
            if len(RegistrationReceipt.objects.filter(answer_sheet_of=registration_form, user=new_mentor)) == 0:
                RegistrationReceipt.objects.create(
                    answer_sheet_of=registration_form,
                    user=new_mentor,
                    answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                    status=RegistrationReceipt.RegistrationStatus.Accepted,
                    is_participating=True)
            return Response(FSMSerializer(context=self.get_serializer_context()).to_representation(fsm),
                            status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: FSMSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=AccountSerializer, permission_classes=[MentorPermission, ])
    def remove_mentor(self, request, pk=None):
        data = request.data
        fsm = self.get_object()
        serializer = AccountSerializer(
            data=data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            deleted_mentor = find_user(serializer.validated_data)
            if deleted_mentor not in fsm.mentors.all():
                raise ParseError(serialize_error('5005'))
            else:
                fsm.mentors.remove(deleted_mentor)
                return Response(FSMSerializer(context=self.get_serializer_context()).to_representation(fsm),
                                status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def get_player_from_team(self, request, pk):
        fsm = self.get_object()
        serializer = TeamGetSerializer(
            data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            team = serializer.validated_data['team']
            player = get_a_player_from_team(team, fsm)
            return Response(PlayerSerializer(context=self.get_serializer_context()).to_representation(player),
                            status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['get'])
    def activate(self, request, pk=None):
        f = self.get_object()
        previous_players = len(f.players.all())
        for r in RegistrationReceipt.objects.filter(is_participating=True):
            if len(Player.objects.filter(user=r.user, fsm=f, receipt=r)) <= 0:
                p = Player.objects.create(user=r.user, fsm=f, receipt=r, current_state=f.first_state,
                                          last_visit=timezone.now())
                PlayerHistory.objects.create(
                    player=p, state=f.first_state, start_time=p.last_visit)

        return Response(data={'new_players_count': len(f.players.all()), 'previous_players_count': previous_players},
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
