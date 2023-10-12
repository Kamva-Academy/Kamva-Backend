from rest_framework.test import APITestCase

from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User, AcademicStudentship, SchoolStudentship
from apps.fsm.models import Event, RegistrationForm, RegistrationReceipt


class InvitationTest(APITestCase):
    def setUp(self):
        a = User.objects.create(phone_number='09134019399', username='a', password=make_password('a'), first_name='a')
        AcademicStudentship.objects.create(user=a), SchoolStudentship.objects.create(user=a)
        b = User.objects.create(phone_number='09134019390', username='b', password=make_password('b'), first_name='b')
        AcademicStudentship.objects.create(user=b), SchoolStudentship.objects.create(user=b)
        form = RegistrationForm.objects.create()
        Event.objects.create(registration_form=form, name='event', event_type='Team', is_approved=True)
        r_a = RegistrationReceipt.objects.create(answer_sheet_of=form, user=a, status='Accepted', is_participating=True)
        r_b = RegistrationReceipt.objects.create(answer_sheet_of=form, user=b, status='Accepted', is_participating=True)

    def test_invite(self):
        event = Event.objects.filter(name='event').first()
        token_a = AccessToken.for_user(User.objects.filter(username='a').first())
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token_a}')
        team_response = self.client.post('/api/fsm/team/', format='json',
                                         data={'name': 'name', 'registration_form': event.registration_form.id})
        self.assertEqual(team_response.status_code, 201)
        invite_response = self.client.post(f'/api/fsm/team/{team_response.data.get("id")}/invite_member/',
                                           format='json', data={'username': 'b'})
        self.assertEqual(invite_response.status_code, 200)
        token_b = AccessToken.for_user(User.objects.filter(username='b').first())
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token_b}')
        r_b = RegistrationReceipt.objects.filter(user__username='b').first()
        my_invitations_response = self.client.get(f'/api/fsm/registration/{event.registration_form.id}/my_invitations/')
        respond_response = self.client.post(f'/api/fsm/invitations/{my_invitations_response.data[0].get("id")}/respond/',
                                             format='json', data={'status': 'Accepted'})
        self.assertEqual(respond_response.status_code, 200)
