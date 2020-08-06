from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json


class BoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'board_%s' % self.room_name

        # Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['data']

        # Send message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'board_message',
                'data': message
            }
        )

    # Receive message from room
    async def board_message(self, event):
        message = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': message
        }))
