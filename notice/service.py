
from django.db import transaction
import requests


TOKEN = 'YOUR_TOKEN'
YOUR_APP_ID = ''

# set header
headers = {
    'Authorization': 'Token ' + TOKEN,
    'Content-Type': 'application/json'
}


class PushNotificationService:
    def __init__(self, notice):
        self.notice = notice

    @transaction.atomic
    def execute(self):
        data = {
            'app_ids': [YOUR_APP_ID, ],
            'data': {
                'title': self.notice.title,
                'content': self.notice.message,
            }
        }
        # send request
        response = requests.post(
            'https://api.pushe.co/v2/messaging/notifications/web/',
            json=data,
            headers=headers,
        )
        self.notice.isPushed = True
        self.notice.save()
        return response
