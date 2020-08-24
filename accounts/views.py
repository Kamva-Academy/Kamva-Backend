import json
import string
from django.contrib.auth.decorators import login_required
from .models import Team
import random
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from accounts.tokens import account_activation_token
from .models import Member, Participant
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


# def check_bibot_response(request):
#     if request.POST.get('bibot-response') is not None:
#         if request.POST.get('bibot-response') != '':
#             r = requests.post('https://api.bibot.ir/api1/siteverify/', data={
#                 'secretkey': '9270bf6cd4a087673ca9e86666977a30',
#                 'response': request.POST['bibot-response']
#             })
#             if r.json()['success']:
#                 return True
#             else:
#                 messages.error(request, 'کپچا به درستی حل نشده است!')
#                 return False
#         else:
#             messages.error(request, 'کپچا به درستی حل نشده است!')
#             return False
#     return False

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, permissions
from rest_framework.views import APIView

from .serializers import MyTokenObtainPairSerializer, MemberSerializer

class ObtainTokenPair(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class GroupSignup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        members_info = request.data['data']
        if type(members_info) is str:
            members_info = json.loads(members_info)

        for member_info in members_info:
            if Member.objects.filter(email__exact=member_info['email']).count() > 0:
                return Response({'success': False, "error":  "فردی با ایمیل "+ member_info['email']+ " قبلا ثبت‌نام کرده"},
                                status=status.HTTP_400_BAD_REQUEST)

        if(members_info[0]['email'] == members_info[1]['email']
                or members_info[1]['email'] == members_info[2]['email']
                or members_info[2]['email'] == members_info[0]['email'] ):
            return Response({'success':False, "error": "ایمیلهای اعضای گروه باید متمایز باشد."}, status=status.HTTP_400_BAD_REQUEST)

        if not (members_info[0]['gender'] == members_info[1]['gender']
                and members_info[2]['gender'] == members_info[1]['gender']):
            return Response({'success':False, "error": "اعضای گروه باید همه دختر یا همه پسر باشند."}, status=status.HTTP_400_BAD_REQUEST)

        if 'document1' not in request.data:
            raise ParseError("Empty content document1")
        doc0 = request.data['document1']
        if 'document2' not in request.data:
            raise ParseError("Empty content document2")
        doc1 = request.data['document2']
        if 'document3' not in request.data:
            raise ParseError("Empty content document3")
        doc2 = request.data['document3']

        member0 = Member.objects.create(
            first_name=members_info[0]['name'],
            username=members_info[0]['email'],
            email=members_info[0]['email'],
            is_active=False,
        )

        member0.set_password(members_info[0]['password'])
        participant0 = Participant.objects.create(
            member=member0,
            gender=members_info[0]['gender'],
            city=members_info[0]['city'],
            school=members_info[0]['school'],
            grade=members_info[0]['grade'],
            phone_number=members_info[0]['phone'],
            document=doc0
        )

        member1 = Member.objects.create(
            first_name=members_info[1]['name'],
            username=members_info[1]['email'],
            email=members_info[1]['email'],
            is_active=False,
        )
        password1 = get_random_alphanumeric_string(8)

        member1.set_password(password1)
        participant1 = Participant.objects.create(
            member=member1,
            gender=members_info[1]['gender'],
            city=members_info[1]['city'],
            school=members_info[1]['school'],
            grade=members_info[1]['grade'],
            phone_number=members_info[1]['phone'],
            document=doc1
        )
        member2 = Member.objects.create(
            first_name=members_info[2]['name'],
            username=members_info[2]['email'],
            email=members_info[2]['email'],
            is_active=False,
        )
        password2 = get_random_alphanumeric_string(8)
        member2.set_password(password2)
        participant2 = Participant.objects.create(
            member=member2,
            gender=members_info[2]['gender'],
            city=members_info[2]['city'],
            school=members_info[2]['school'],
            grade=members_info[2]['grade'],
            phone_number=members_info[2]['phone'],
            document=doc2
        )

        team = Team()
        participant0.team = team
        participant1.team = team
        participant2.team = team
        team.save()
        member0.save()
        participant0.save()
        member1.save()
        participant1.save()
        member2.save()
        participant2.save()

        absolute_uri = request.build_absolute_uri('/')[:-1].strip("/")
        member0.send_signup_email(absolute_uri)
        member1.send_signup_email(absolute_uri, password1)
        member2.send_signup_email(absolute_uri, password2)

        return Response({'success': True}, status=status.HTTP_200_OK)


class IndividualSignup(APIView):
    parser_class = (MultiPartParser,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if Member.objects.filter(email__exact=request.data['email']).count() > 0:
            return Response({'success': False, "error": "فردی با ایمیل " + request.data['email'] + "قبلا ثبت‌نام کرده"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if 'document' not in request.data:
            raise ParseError("Empty Document content")

        doc = request.data['document']

        member = Member.objects.create(
            first_name=request.data['name'],
            username=request.data['email'],
            email=request.data['email'],
            is_active=False,

        )
        member.set_password(request.data['password'])
        participant = Participant.objects.create(
            member=member,
            gender=request.data['gender'],
            city=request.data['city'],
            school=request.data['school'],
            grade=request.data['grade'],
            phone_number=request.data['phone'],
            document=doc
        )
        member.save()
        participant.save()

        absolute_uri = request.build_absolute_uri('/')[:-1].strip("/")

        member.send_signup_email(absolute_uri)
        return Response({'success': True}, status=status.HTTP_200_OK)


@login_required
def logout(request):
    auth_logout(request)
    return Response({'success': True}, status=status.HTTP_200_OK)


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def _redirect_homepage_with_action_status(action='payment', status=settings.OK_STATUS):
    response = redirect('/')
    response['Location'] += '?%s=%s' % (action, status)
    return response


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        member = Member.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Member.DoesNotExist):
        member = None
    if member is not None and account_activation_token.check_token(member, token):
        member.is_active = True
        member.save()
        member_team = member.participant.team
        if member_team is not None:
            team_active = True
            for participant in member_team.participant_set.all():
                if not participant.member.is_active:
                    team_active = False
            member_team.active = team_active
            member_team.save()

        auth_login(request, member)
        token = MyTokenObtainPairSerializer.get_token(member)
        # return redirect('home')
        return _redirect_homepage_with_action_status('activate', settings.OK_STATUS)
    elif member is not None and member.is_active:
        return _redirect_homepage_with_action_status('activate', settings.HELP_STATUS)
    else:
        return _redirect_homepage_with_action_status('activate', settings.ERROR_STATUS)


class ChangePass(APIView):

    def post(self, request):
        user = JWTAuthentication.get_user(self,JWTAuthentication.get_validated_token(self,JWTAuthentication.get_raw_token(self,JWTAuthentication.get_header(JWTAuthentication,request))))
        new_pass = request.data['newPass']
        # username = request.POST.get('username')
        # member = get_object_or_404(Member, username=username)
        user.set_password(new_pass)
        user.save()


        return Response({'success': True},status=status.HTTP_200_OK)


class UploadAnswerView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        file = request.data['file']
        user = JWTAuthentication.get_user(self,JWTAuthentication.get_validated_token(self,JWTAuthentication.get_raw_token(self,JWTAuthentication.get_header(JWTAuthentication,request))))
        username = user.username
        participant = get_object_or_404(Member, username = username).participant
        participant.ent_answer = file
        participant.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)