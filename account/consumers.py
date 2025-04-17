# consumer
import json
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db import transaction
from channels.db import database_sync_to_async

from .models import MessageUser, User


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'take':
            message_id = data.get('id')
            user = self.scope["user"]

            user = self.scope["user"]

            @database_sync_to_async
            def try_take(taken_by_user=None):
                with transaction.atomic():
                    try:
                        msg = MessageUser.objects.select_for_update().get(id=message_id)
                        if msg.taken_by is None:
                            msg.taken_by = taken_by_user
                            msg.save()
                            return True
                    except MessageUser.DoesNotExist:
                        pass
                    return False

            success = await try_take()

            if success:
                # faqat xabarni o‘zgartirgan userdan boshqalarga yuborish uchun
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_delete',
                        'id': message_id,
                        'exclude_channel': self.channel_name
                    }
                )
            else:
                # already taken, jo'natmaslik mumkin
                pass

        elif action == 'send':
            message = data.get('message')

            # xabarni saqlash
            @sync_to_async
            def save_message():
                msg = MessageUser.objects.create(text=message)
                return msg.id, msg.text

            msg_id, msg_text = await save_message()

            # barcha clientlarga yangi xabar yuborish
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg_text,
                    'id': msg_id
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'id': event['id'],
            'taken_by': None  # yangisida hali yo‘q
        }))

    async def chat_delete(self, event):
        if self.channel_name != event['exclude_channel']:
            await self.send(text_data=json.dumps({
                'type': 'delete',
                'id': event['id']
            }))
