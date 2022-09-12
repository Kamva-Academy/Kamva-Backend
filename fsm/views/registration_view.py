import csv
from io import BytesIO, StringIO

import rest_framework.parsers
from django.contrib.auth.hashers import make_password
from django.db.models import Count, F, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.parsers import MultiPartParser

from accounts.models import User, SchoolStudentship, Studentship, AcademicStudentship
from accounts.serializers import UserSerializer
from accounts.utils import create_or_update_user, create_registration_receipt, create_team
from errors.error_codes import serialize_error
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer, RegistrationInfoSerializer, \
    RegistrationPerCitySerializer
from fsm.serializers.paper_serializers import RegistrationFormSerializer, ChangeWidgetOrderSerializer
from fsm.serializers.certificate_serializer import CertificateTemplateSerializer
from fsm.models import RegistrationForm, transaction, RegistrationReceipt, Invitation, AnswerSheet, Team
from fsm.permissions import IsRegistrationFormModifier
from fsm.serializers.serializers import BatchRegistrationSerializer
from fsm.serializers.team_serializer import InvitationSerializer
from fsm.pagination import RegistrationReceiptSetPagination


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationFormSerializer
    queryset = RegistrationForm.objects.all()
    my_tags = ['registration']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    def get_permissions(self):
        if self.action in ['create', 'register', 'list', 'get_possible_teammates', 'my_invitations']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsRegistrationFormModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: CertificateTemplateSerializer}, tags=my_tags + ['certificates'])
    @action(detail=True, methods=['get'])
    def view_certificate_templates(self, request, pk=None):
        registration_form = self.get_object()
        return Response(
            data=CertificateTemplateSerializer(registration_form.certificate_templates.all(), many=True,
                                               context=self.get_serializer_context()).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: RegistrationInfoSerializer})
    @action(detail=True, methods=['get'])
    def receipts(self, request, pk=None):
        queryset = self.get_object().registration_receipts.all()
        paginator = RegistrationReceiptSetPagination()
        page_queryset = paginator.paginate_queryset(queryset, request)
        if page_queryset is not None:
            serializer = RegistrationInfoSerializer(page_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: RegistrationPerCitySerializer})
    @action(detail=True, methods=['get'])
    def registration_count_per_city(self, request, pk=None):
        results = RegistrationReceipt.objects.filter(answer_sheet_of=self.get_object()).annotate(
            city=F('user__city')).values('city').annotate(registration_count=Count('id'))
        return Response(RegistrationPerCitySerializer(results, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: RegistrationInfoSerializer})
    @action(detail=True, methods=['get'])
    def possible_teammates(self, request, pk=None):
        user = self.request.user
        registration_form = self.get_object()

        self_receipts = RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                                           is_participating=True)
        if len(self_receipts) < 1:
            raise ParseError(serialize_error('4050'))

        if not user.gender or (user.gender != User.Gender.Male and user.gender != User.Gender.Female):
            raise ParseError(serialize_error('4058'))
        if registration_form.gender_partition_status == RegistrationForm.GenderPartitionStatus.BothNonPartitioned:
            receipts = registration_form.registration_receipts.exclude(pk__in=self_receipts).filter(
                Q(team__isnull=True) | Q(team__exact=''), is_participating=True)
        else:
            receipts = registration_form.registration_receipts.exclude(pk__in=self_receipts).filter(
                Q(team__isnull=True) | Q(team__exact=''), is_participating=True, user__gender=user.gender)
        return Response(RegistrationInfoSerializer(receipts, many=True).data, status=status.HTTP_200_OK)

    @transaction.atomic
    @swagger_auto_schema(responses={200: InvitationSerializer}, tags=['teams'])
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_invitations(self, request, pk=None):
        receipt = RegistrationReceipt.objects.filter(user=request.user, is_participating=True,
                                                     answer_sheet_of=self.get_object()).first()
        invitations = Invitation.objects.filter(
            invitee=receipt, team__registration_form=self.get_object(), status=Invitation.InvitationStatus.Waiting)
        return Response(data=InvitationSerializer(invitations, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: RegistrationFormSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=ChangeWidgetOrderSerializer)
    def change_order(self, request, pk=None):
        serializer = ChangeWidgetOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.get_object().set_widget_order(serializer.validated_data.get('order'))
        return Response(data=RegistrationFormSerializer(self.get_object()).data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(responses={201: RegistrationReceiptSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=RegistrationReceiptSerializer)
    def register(self, request, pk=None):
        context = self.get_serializer_context()
        context['answer_sheet_of'] = self.get_object()
        serializer = RegistrationReceiptSerializer(data={'answer_sheet_type': 'RegistrationReceipt',
                                                         **request.data}, context=context)
        if serializer.is_valid(raise_exception=True):
            register_permission_status = self.get_object(
            ).user_permission_status(context.get('user', None))
            if register_permission_status == RegistrationForm.RegisterPermissionStatus.DeadlineMissed:
                raise ParseError(serialize_error('4036'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotStarted:
                raise ParseError(serialize_error('4100'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.StudentshipDataIncomplete:
                raise PermissionDenied(serialize_error('4057'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotPermitted:
                raise PermissionDenied(serialize_error('4032'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.GradeNotAvailable:
                raise ParseError(serialize_error('4033'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.StudentshipDataNotApproved:
                raise ParseError(serialize_error('4034'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotRightGender:
                raise ParseError(serialize_error('4109'))
            elif register_permission_status == RegistrationForm.RegisterPermissionStatus.Permitted:
                serializer.validated_data['answer_sheet_of'] = self.get_object(
                )
                registration_receipt = serializer.save()

                form = registration_receipt.answer_sheet_of
                event = form.event
                # TODO - handle fsm sign up
                if event:
                    if event.maximum_participant is None or len(event.participants) < event.maximum_participant:
                        if form.accepting_status == RegistrationForm.AcceptingStatus.AutoAccept:
                            registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
                            if not event.merchandise:
                                registration_receipt.is_participating = True
                            registration_receipt.save()
                        elif form.accepting_status == RegistrationForm.AcceptingStatus.CorrectAccept:
                            if registration_receipt.correction_status() == RegistrationReceipt.CorrectionStatus.Correct:
                                registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
                                if not event.merchandise:
                                    registration_receipt.is_participating = True
                                registration_receipt.save()
                    else:
                        registration_receipt.status = RegistrationReceipt.RegistrationStatus.Rejected
                        registration_receipt.save()
                        raise ParseError(serialize_error('4035'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)


GENDER_MAPPING = {
    'دختر': User.Gender.Female,
    'پسر': User.Gender.Male
}

GRADE_MAPPING = {
    'نهم': 9,
    'دهم': 10,
    'یازدهم': 11,
    'دوازدهم': 12
}

MAJOR_MAPPING = {
    'ریاضی': SchoolStudentship.Major.Math,
    'تجربی': SchoolStudentship.Major.Biology,
    'ادبیات': SchoolStudentship.Major.Literature,
    'عمومی': SchoolStudentship.Major.Others
}


def convert_with_punctuation_removal(string):
    return string.replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace(
        '۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9').replace(' ', '').replace(
        '-', '').replace('_', '')


class RegistrationAdminViewSet(GenericViewSet):
    queryset = RegistrationForm.objects.all()
    serializer_class = BatchRegistrationSerializer
    # parser_classes = [MultiPartParser]
    permission_classes = [IsRegistrationFormModifier]
    my_tags = ['registration']

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def register_csv(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            in_memory_file = request.data.get('file')
            registration_form = self.get_object()

            file = in_memory_file.read().decode('utf-8')
            for data in csv.DictReader(StringIO(file)):
                member = dict()
                for k in data.keys():
                    member[k] = data[k]

                team_name = member['team_name']
                grade = member['grade']
                chat_room = member['chat_room']

                if team_name is not None:
                    team = create_team(team_name=team_name,
                                       registration_form=registration_form)

                user = create_or_update_user(**data)

                if len(SchoolStudentship.objects.filter(user=user)) <= 0:
                    school_studentship = SchoolStudentship.objects.create(
                        studentship_type=Studentship.StudentshipType.School,
                        user=user,
                        major=MAJOR_MAPPING[member['major']] if 'major' in member.keys() else MAJOR_MAPPING[
                            'ریاضی'],
                        grade=grade,
                        is_document_verified=True,
                    )

                if len(AcademicStudentship.objects.filter(user=user)) <= 0:
                    academic_studentship = AcademicStudentship.objects.create(
                        studentship_type=Studentship.StudentshipType.Academic,
                        user=user,
                    )

                receipt = create_registration_receipt(user, registration_form)

                if team_name is not None and team_name != "":
                    team_with_same_head = Team.objects.filter(
                        team_head=receipt).first()
                    if team_with_same_head is not None:
                        team_with_same_head.team_head = None
                        team_with_same_head.save()
                    if team.team_head is None:
                        team.team_head = receipt
                    if chat_room != "":
                        team.chat_room = chat_room
                    team.save()
                    receipt.team = team
                    receipt.save()

            return Response("ok", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def register_individual(self, request, pk=None):
        user = create_or_update_user(**request.data)
        registration_form = self.get_object()
        receipt = create_registration_receipt(user, registration_form)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
