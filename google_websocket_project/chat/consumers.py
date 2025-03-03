import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['url_route']['kwargs']['token']
        self.user = await self.get_user_from_token(token)
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"chat_{min(self.user.id, int(self.other_user_id))}_{max(self.user.id, int(self.other_user_id))}"

        if self.user.is_anonymous:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver_id = text_data_json['receiver_id']

        if not message:
            return
        
        receiver = await self.get_user(receiver_id)

        if receiver:
            await self.send_message(self.user.id, receiver.id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': self.user.id,
                    'receiver_id': receiver.id,
                    'username': self.user.username
                }
            )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'username': event['username'],
        }))
    
    @database_sync_to_async
    def send_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=sender, receiver=receiver, content=content)
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return None
        try:
            access_token = AccessToken(token)
            return User.objects.get(id=access_token['user_id'])
        except User.DoesNotExist:
            return None
