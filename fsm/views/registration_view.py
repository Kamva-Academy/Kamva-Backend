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
from errors.error_codes import serialize_error
from fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer, RegistrationInfoSerializer, \
    RegistrationPerCitySerializer
from fsm.serializers.paper_serializers import RegistrationFormSerializer, ChangeWidgetOrderSerializer
from fsm.serializers.certificate_serializer import CertificateTemplateSerializer
from fsm.models import RegistrationForm, transaction, RegistrationReceipt, Invitation, AnswerSheet, Team
from fsm.permissions import IsRegistrationFormModifier
from fsm.serializers.serializers import BatchRegistrationSerializer
from fsm.serializers.team_serializer import InvitationSerializer


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
        return Response(data=RegistrationInfoSerializer(self.get_object().registration_receipts, many=True).data,
                        status=status.HTTP_200_OK)

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
    parser_classes = [MultiPartParser]
    permission_classes = [IsRegistrationFormModifier]
    my_tags = ['registration']

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def batch_register(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            in_memory_file = request.data.get('file')
            registration_form = self.get_object()
            older_users = []
            result_teams = []
            result_users = []
            file = in_memory_file.read().decode('utf-8')
            for data in csv.DictReader(StringIO(file)):
                members = [dict(), dict(), dict()]
                for k in data.keys():
                    if k == 'gender':
                        for i in range(len(members)):
                            members[i][k] = data[k].strip()
                    if k in ['phone_number', 'national_code', 'name', 'grade']:
                        for i in range(len(members)):
                            if len(data[k]) > 1:
                                members[i][k] = data[k].split('-')[i].strip()
                receipts = []
                for member in members:
                    if 'phone_number' not in member.keys():
                        continue
                    phone_number = convert_with_punctuation_removal(
                        member['phone_number'])
                    national_code = convert_with_punctuation_removal(
                        member['national_code'])
                    first_name = member['name'].split()[0]
                    last_name = member['name'][len(first_name):].strip()
                    grade = convert_with_punctuation_removal(member['grade'])
                    if len(User.objects.filter(Q(username=national_code) | Q(phone_number=phone_number))) <= 0:
                        user = User.objects.create(
                            phone_number=phone_number,
                            first_name=first_name,
                            last_name=last_name,
                            password=make_password(national_code),
                            national_code=national_code,
                            username=national_code,
                            gender=GENDER_MAPPING[member['gender']],
                        )
                    elif len(User.objects.filter(phone_number=phone_number)) > 0:
                        user = User.objects.filter(
                            phone_number=phone_number).first()
                        older_users.append(user.username)
                    else:
                        user = User.objects.filter(
                            username=national_code).first()
                    if len(SchoolStudentship.objects.filter(user=user)) <= 0:
                        school_studentship = SchoolStudentship.objects.create(
                            studentship_type=Studentship.StudentshipType.School,
                            user=user,
                            major=MAJOR_MAPPING[member['major']] if 'major' in member.keys() else MAJOR_MAPPING[
                                'ریاضی'],
                            grade=grade,
                            is_document_verified=True,
                        )
                    else:
                        school_studentship = SchoolStudentship.objects.filter(
                            user=user).first()
                    if len(AcademicStudentship.objects.filter(user=user)) <= 0:
                        academic_studentship = AcademicStudentship.objects.create(
                            studentship_type=Studentship.StudentshipType.Academic,
                            user=user,
                        )
                    else:
                        academic_studentship = AcademicStudentship.objects.filter(
                            user=user).first()
                    if len(RegistrationReceipt.objects.filter(answer_sheet_of=registration_form, user=user)) <= 0:
                        receipts.append(RegistrationReceipt.objects.create(
                            answer_sheet_of=registration_form,
                            answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                            user=user,
                            status=RegistrationReceipt.RegistrationStatus.Accepted,
                            is_participating=True,
                        ))
                    else:
                        receipts.append(RegistrationReceipt.objects.filter(
                            answer_sheet_of=registration_form, user=user).first())
                    result_users.append(user.username)
                if len(Team.objects.filter(name=data['team_code'])) <= 0:
                    team = Team.objects.create(name=data['team_code'],
                                               team_head=receipts[0],
                                               registration_form=registration_form)
                else:
                    team = Team.objects.filter(name=data['team_code']).first()

                for x in receipts:
                    x.team = team
                    x.save()
                result_teams.append(team.name)
            return Response({'users': result_users, 'older_users': older_users, 'teams': result_teams},
                            status=status.HTTP_200_OK)

    def create_user_from_csv(self, data):
        member = dict()
        for k in data.keys():
            member[k] = data[k].strip()

        username = member['username']
        phone_number = member['phone_number']
        password = member['password']
        first_name = member['first_name']
        last_name = member['last_name']

        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                password=password,
            )

        if password is None:
            user.password = username
            user.save()

        return user

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def csv_registration(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            in_memory_file = request.data.get('file')
            registration_form = self.get_object()

            file = in_memory_file.read().decode('utf-8')
            for data in csv.DictReader(StringIO(file)):
                user = self.create_user_from_csv(data)
                member = dict()
                for k in data.keys():
                    member[k] = data[k].strip()

                team_name = member['team_name']
                gender = member['gender']
                grade = member['grade']

                if team_name is not None:
                    team = Team.objects.filter(name=team_name).first()
                    if team is None:
                        team = Team.objects.create(
                            registration_form=registration_form)
                        team.name = team_name
                        team.save()

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

                receipt = RegistrationReceipt.objects.filter(
                    answer_sheet_of=registration_form, user=user).first()

                if receipt is None:
                    receipt = RegistrationReceipt.objects.create(
                        answer_sheet_of=registration_form,
                        answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                        user=user,
                        status=RegistrationReceipt.RegistrationStatus.Accepted,
                        is_participating=True,
                    )

                if team_name is not None:
                    if team.team_head is None:
                        team.team_head = receipt
                        team.save()
                    receipt.team = team
                    receipt.save()

            return Response("ok", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def add_individual_student(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            in_memory_file = request.data.get('file')

            file = in_memory_file.read().decode('utf-8')
            for data in csv.DictReader(StringIO(file)):
                self.create_user_from_csv(data)
                
        return Response("ok", status=status.HTTP_200_OK)
