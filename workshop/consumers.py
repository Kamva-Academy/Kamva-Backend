from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message
from accounts.models import Member, Participant, Teamm
from .views import get_last_10_messages, get_user_contact, get_current_chat, get_message_by_id
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

import logging
logger = logging.getLogger(__name__)


def get_name(team_uuid, person_uuid):
    try:
        # TODO kinda access uuid
        member = Member.objects.filter(uuid=person_uuid)
        logger.info(f'try to access team_uuid {team_uuid}')
        if member:
            if member[0].is_mentor:
                result = True
            elif member[0].is_participant:
                participant = Participant.objects.get(member=member[0])
                try:
                    team = Teamm.objects.get(uuid=team_uuid)
                except:
                    return False
                if participant in team.team_members.all():
                    result = True
                else:
                    result = False
            else:
                result = False
        else:
            result = False
        return result
    except:
        return False


class BoardConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['team_uuid']
        person_uuid = self.scope['url_route']['kwargs']['person_uuid']
        self.room_group_name = 'board_%s' % self.room_name
        check_user = await database_sync_to_async(get_name)(self.room_name, person_uuid)
        if check_user:
            # Join room
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('data')
        message_type = text_data_json.get('type')
        # Send message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'data': message
            }
        )

    # Receive message from room
    async def PASS_DRAWING_STATE(self, event):
        message = event.get('data')
        message_type = event.get('type')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': message,
            'type': message_type
        }))

    # Receive message from room
    async def JOIN_TO_GROUP_ROOM(self, event):
        message = event.get('data')
        message_type = event.get('type')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': message,
            'type': message_type
        }))


class ChatConsumer(WebsocketConsumer):

    def connect(self):
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
        message = data.get('data')
        message_type = data.get('type')
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': message_type,
                'data': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_fetch_messages(self, event):
        data = event.get('data')
        index = int(data.get('index', 0))
        messages = get_last_10_messages(data['chatId'], index)

        content = {
            'type': event.get('type'),
            'data': self.messages_to_json(messages)
        }
        self.send_message(content)

    def chat_new_message(self, event):
        data = event.get('data')
        user_contact = get_user_contact(data['from'])
        parent_id = data.get('parentId', None)
        if parent_id is not None:
            message_parent = get_message_by_id(parent_id)
        else:   message_parent = None
        message = Message.objects.create(
            contact=user_contact,
            content=data['message'],
            parent=message_parent)
        current_chat = get_current_chat(data['chatId'])

        current_chat.messages.add(message)
        current_chat.save()
        content = {
            'type': event.get('type'),
            'data': self.message_to_json(message)
        }
        return self.send_message(content)

    def chat_seen_message(self, event):
        data = event.get('data')
        message = get_message_by_id(data['messageId'])
        current_chat = get_current_chat(data['chatId'])
        chat_messages = current_chat.messages
        chat_messages.update(seen = True)
        content = {
            'type': event.get('type'),
            'data':{'success': True}}
        return self.send_message(content)

    def chat_fetch_single_message(self, event):
        data = event.get('data')
        message = get_message_by_id(data['messageId'])
        content = {
            'type': event.get('type'),
            'data': self.message_to_json(message)
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

