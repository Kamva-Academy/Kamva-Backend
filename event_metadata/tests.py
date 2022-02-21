from urllib import response
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from event_metadata.models import StaffInfo
from accounts.models import User
from django.urls import reverse
# Create your tests here.
from fsm.models import Event

class EventMetaDataTest(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.event1 = Event.objects.create()
        self.event2 = Event.objects.create()
        self.account = User.objects.create()
        self.staff_info1 = StaffInfo.objects.create(account=self.account, event=self.event1, description="111")
        self.staff_info2 = StaffInfo.objects.create(account=self.account, event=self.event1, description="222")
        self.staff_info3 = StaffInfo.objects.create(account=self.account, event=self.event1, description="333")
        self.staff_info4 = StaffInfo.objects.create(account=self.account, event=self.event2, description="444")
        self.staff_info5 = StaffInfo.objects.create(account=self.account, event=self.event2, description="555")
        
    
