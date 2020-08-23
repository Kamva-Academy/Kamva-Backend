import string

from .models import Team
import re
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.tokens import account_activation_token
from .forms import SignUpForm\
    # , strip_spaces_between_tags, render_to_string
from .models import Member, Participant


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
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MyTokenObtainPairSerializer, MemberSerializer

class ObtainTokenPair(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class GroupSignup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        members_info = request.data['data']

        for member_info in members_info:
            if Member.objects.filter(email__exact=member_info['email']).count() > 0:
                return Response({'success': False, "error":  "فردی با ایمیل "+ member_info['email']+ "قبلا ثبت‌نام کرده"},
                                status=status.HTTP_400_BAD_REQUEST)

        if(members_info[0]['email'] == members_info[1]['email']
                or members_info[1]['email'] == members_info[2]['email']
                or members_info[2]['email'] == members_info[0]['email'] ):
            return Response({'success':False, "error": "ایمیلهای اعضای گروه باید متمایز باشد."}, status=status.HTTP_400_BAD_REQUEST)

        if not (members_info[0]['gender'] == members_info[1]['gender']
                and members_info[2]['gender'] == members_info[1]['gender']):
            return Response({'success':False, "error": "اعضای گروه باید همه دختر یا همه پسر باشند."}, status=status.HTTP_400_BAD_REQUEST)

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
            # document=form.cleaned_data['document']
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
            # document=form.cleaned_data['document']
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
            # document=form.cleaned_data['document']
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
        print(absolute_uri)
        member0.send_signup_email(absolute_uri)
        member1.send_signup_email(absolute_uri, password1)
        member2.send_signup_email(absolute_uri, password2)



        return Response({'success': True}, status=status.HTTP_200_OK)




        # serializer = MemberSerializer(data=request.data)
        # if serializer.is_valid():
        #     user = serializer.save()
        #     if user:
        #         json = serializer.data
        #         return Response(json, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IndividualSignup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        if Member.objects.filter(email__exact=request.data['email']).count() > 0:
            return Response({'success': False, "error": "فردی با ایمیل " + request.data['email'] + "قبلا ثبت‌نام کرده"},
                            status=status.HTTP_400_BAD_REQUEST)
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
            # document=form.cleaned_data['document']
        )
        member.save()
        participant.save()

        #TODO send verify email

        #TODO response (with tokem)
        return Response({'success': True}, status=status.HTTP_200_OK)


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    print("Random alphanumeric String is:", result_str)

#
# @api_view(['POST'])
# def signup(request):
#     if request.user.is_authenticated:
#         pass
#     # if not SiteConfiguration.get_solo().is_signup_enabled:
#     #     return redirect('homepage:homepage')
#     if request.method == 'POST' :
#         data = request.data
#             # and check_bibot_response(request):
#         form = SignUpForm(request.POST, request.FILES)
#         if not form.is_valid():
#             messages.add_message(request, messages.ERROR, 'ایمیل تکراری')
#             return render(request, 'auth/signup.html')
#
#         # file = open('animals.txt', 'r', encoding='UTF-8')
#         # animals = file.read().strip().split('\n')
#         # file.close()
#         # file = open('adjectives.txt', 'r', encoding='UTF-8')
#         # adjectives = file.read().strip().split('\n')
#         # file.close()
#
#         # username = random.choice(animals) + ' ' + random.choice(adjectives)
#         # while Member.objects.filter(username__exact=username).count() > 0:
#             # username = random.choice(animals) + ' ' + random.choice(adjectives)
#
#         member = Member.objects.create(
#             first_name=request.POST['name'],
#             username=request.POST['email'],
#             email=request.POST['email'],
#             is_active=False,
#         )
#         member.set_password(request.POST['password'])
#         participant = Participant.objects.create(
#             member=member,
#             gender=request.POST['gender'],
#             city=request.POST['city'],
#             school=request.POST['school'],
#             grade=request.POST['grade'],
#             phone_number=request.POST['phone'],
#             document=form.cleaned_data['document']
#         )
#         member.save()
#         participant.save()
#         token = account_activation_token.make_token(member)
#         html_content = strip_spaces_between_tags(render_to_string('auth/signup_email.html', {
#             'user': member,
#             'base_url': request.build_absolute_uri(reverse('homepage:homepage'))[:-1],
#             'token': token,
#             'uid': urlsafe_base64_encode(force_bytes(member.pk))
#         }))
#         text_content = re.sub('<style[^<]+?</style>', '', html_content)
#         text_content = strip_tags(text_content)
#
#         msg = EmailMultiAlternatives('تایید ثبت‌نام اولیه', text_content, 'Rastaiha <info@rastaiha.ir>', [member.email])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#         # return _redirect_homepage_with_action_status('signup', settings.OK_STATUS)
#     # return render(request, 'auth/signup.html')
#     token = Token.objects.create(user=accounts.models.Member)
#     return Response({'token': token.key}, status=status.HTTP_201_CREATED)

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
        auth_login(request, member)
        # return redirect('home')
        return _redirect_homepage_with_action_status('activate', settings.OK_STATUS)
    elif member is not None and member.is_active:
        return _redirect_homepage_with_action_status('activate', settings.HELP_STATUS)
    else:
        return _redirect_homepage_with_action_status('activate', settings.ERROR_STATUS)
