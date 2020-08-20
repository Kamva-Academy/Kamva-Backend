from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.shortcuts import get_object_or_404

from .models import Message, Chat, Contact
from .views import get_last_10_messages, get_user_contact, get_current_chat, get_message_by_id
from channels.generic.websocket import AsyncJsonWebsocketConsumer

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        print(data)
        print("fetching")
        print("---------------------gggggggggggggggggggggggggg-----------------------")
        index = int(data.get('index', 0))
        messages = get_last_10_messages(data['chatId'], index)

        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data['from'])
        message_parent = get_message_by_id(data['parentId'])
        message = Message.objects.create(
            contact=user_contact,
            content=data['message'],
            parent=message_parent)
        current_chat = get_current_chat(data['chatId'])

        current_chat.messages.add(message)
        current_chat.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def seen_message(self, data):
        message = get_message_by_id(data['messageId'])
        current_chat = get_current_chat(data['chatId'])
        chat_messages = current_chat.messages
        chat_messages.update(seen = True)
        print("--------------seen all messages of chat-------------")
        content = {
            "command": "seen_message",
            "success": True}
        return self.send_message(content)

    def fetch_single_message(self, data):
        message = get_message_by_id(data['messageId'])
        content = {
            "command": "fetch_single_message",
            "message": self.message_to_json(message)
        }
        return self.send_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        prentId = message.parent_id
        return {
            'id': message.id,
            'author': message.contact.user.username,
            'content': message.content,
            'timestamp': str(message.timestamp),
            'seen': str(message.seen),
            'parent': str(message.parent_id)
        }

    def connect(self):
        print("-------------connecting-------------------")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'seen_message': seen_message,
        'fetch_single_message': fetch_single_message
    }