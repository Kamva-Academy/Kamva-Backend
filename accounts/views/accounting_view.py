import logging

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import VerificationCode, User
from accounts.permissions import IsHimself
from accounts.serializers import PhoneNumberSerializer, UserSerializer, VerificationCodeSerializer, AccountSerializer, \
    MyTokenObtainPairSerializer
from accounts.utils import find_user
from errors.error_codes import serialize_error

logger = logging.getLogger(__name__)


class SendVerificationCode(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PhoneNumberSerializer
    my_tags = ['accounts']

    @swagger_auto_schema(operation_description="Sends verification code to verify phone number or change password",
                         responses={200: "Verification code sent successfully",
                                    400: "error code 4000 for not being digits & 4001 for phone length less than 10",
                                    404: "error code 4008 for not finding user to change password",
                                    500: "error code 5000 for problems in sending SMS",
                                    })
    @transaction.atomic
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data.get('phone_number', None)
            verification_code = VerificationCode.objects.create_verification_code(phone_number=phone_number)
            # try:
            #     verification_code.send_sms(serializer.validated_data.get('code_type', None))
            # except:
            #     raise ServiceUnavailable(serialize_error('5000'))
            return Response({'detail': 'Verification code sent successfully'}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    parser_classes = (MultiPartParser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializer_action_classes = {
        'create': VerificationCodeSerializer
    }
    my_tags = ['accounts']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsHimself]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return User.objects.none()
        elif user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    @swagger_auto_schema(responses={201: AccountSerializer,
                                    400: "error code 4002 for len(code) < 5, 4003 for invalid code, "
                                         "4004 for previously submitted users & 4005 for expired code",
                                    })
    @transaction.atomic
    def create(self, request):
        data = request.data
        serializer = VerificationCodeSerializer(data=data)
        if serializer.is_valid(raise_exception=True):

            phone_number = serializer.validated_data.get('phone_number', None)
            if User.objects.filter(phone_number__exact=phone_number).count() > 0:
                raise ParseError(serialize_error('4004', {'param1': phone_number}))

            serializer = AccountSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                token_serializer = MyTokenObtainPairSerializer(
                    data={'password': request.data.get('password'), 'username': user.username})
                if token_serializer.is_valid(raise_exception=True):
                    return Response({'account': serializer.data, **token_serializer.validated_data},
                                    status=status.HTTP_201_CREATED)


class Login(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(tags=['accounts'],
                         responses={201: AccountSerializer,
                                    400: "error code 4007 for not enough credentials",
                                    401: "error code 4006 for not submitted users & 4009 for wrong credentials"})
    def post(self, request, *args, **kwargs):
        data = request.data
        user = find_user(data)
        serializer = self.get_serializer(data=data)
        try:
            if serializer.is_valid(raise_exception=True):
                return Response({'account': AccountSerializer(user).data, **serializer.validated_data},
                                status=status.HTTP_200_OK)
        except TokenError as e:
            raise InvalidToken(e.args[0])


class ChangePassword(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerificationCodeSerializer

    @swagger_auto_schema(tags=['accounts'],
                         responses={200: AccountSerializer,
                                    400: "error code 4002 for len(code) < 5, 4003 for invalid & 4005 for expired code",
                                    })
    @transaction.atomic
    def post(self, request):
        data = request.data
        serializer = VerificationCodeSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data.get('phone_number', None)
            users = User.objects.filter(phone_number__exact=phone_number)
            if users.count() <= 0:
                raise NotFound(serialize_error('4008'))

            user = users.first()
            serializer = AccountSerializer(instance=user, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)