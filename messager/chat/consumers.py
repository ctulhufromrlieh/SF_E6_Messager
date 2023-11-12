from channels.consumer import AsyncConsumer, SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.core import serializers
# from channels.auth import channel_session_user_from_http
# from channels import Group
import json
from django.db.models import F
from asgiref.sync import async_to_sync

from chat.models import Profile, ChatRoom


# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         # await self.send({"type": "websocket.accept"})
#         await self.send({"type": "websocket.accept"})
#
#     async def websocket_receive(self, text_data):
#         await self.send({
#             "type": "websocket.send",
#             "text": "Hello from Django socket"
#         })
#
#     async def websocket_disconnect(self, event):
#         pass

class ChatConsumer(SyncConsumer):
# class ChatConsumer(JsonWebsocketConsumer):
# class ChatComusmer(WebsocketConsumer):
#     channel_layer_alias = 'events'

    @classmethod
    def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content)

    @classmethod
    def get_input_data(cls, text_data):
        # print(text_data)
        # data = cls.decode_json(text_data)
        if 'text' not in text_data:
            return

        data = cls.decode_json(text_data['text'])
        # print(data)
        # print(type(data))
        if 'get' in data:
            # print('get in data')
            return 'get', data['get']

    @classmethod
    def get_profile_id_by_user_id(cls, user_id):
        return Profile.objects.get(user__id=user_id).id

    def get_user_list(self, my_profile_id):
        qs = Profile.objects.all()
        # print(list(qs))
        qs = qs.exclude(id=my_profile_id)
        # print(list(qs))
        # qs = Profile.objects.all().exclude(id=my_id)
        values = qs.annotate(username=F('user__username')).values("id", "username", )
        # values = qs.values("id", "user__username", )
        lst = list(values)
        # print(lst)
        # return self.encode_json(lst)
        return lst;

    def get_room_list(self):
        qs = ChatRoom.objects.all()
        values = qs.values("id", "name", )
        lst = list(values)
        # print(lst)
        # return self.encode_json(lst)
        return lst;


    def websocket_connect(self, event):
        # self.send({"type": "websocket.accept"})
        # self.room_group_name = 'chat'
        print(self.channel_layer)
        async_to_sync(self.channel_layer.group_add)("events", self.channel_name)
        profile_id = self.scope['user'].profile.id
        single_channel_name = f"single_user_group_{profile_id}"

        print("websocket_connect")

        # count = getattr(self.channel_layer, self.group_name, 0)
        # print(count)

        # print(self.channel_layer)

        # async_to_sync(self.channel_layer.group_add)(
        #     'events',
        #     self.channel_name
        #     # 'events'
        # )

        # self.accept()

        # count = getattr(self.channel_layer, self.group_name, 0)
        # print(count)

        # self.channel_layer.group_add(
        #     self.room_group_name,
        #     single_channel_name
        # )

        # await self.send({"type": "websocket.accept"})
        self.send({"type": "websocket.accept"})

    def websocket_receive(self, text_data):
        # print(text_data)
        cmd_type, cmd_arg = self.get_input_data(text_data)

        user = self.scope['user']
        profile_id = self.get_profile_id_by_user_id(user.id)
        print(f"user.id = {user.id}")
        print(f"profile.id = {self.get_profile_id_by_user_id(user.id)}")
        if not user.is_authenticated:
            return

        if cmd_type == "get":
            if cmd_arg == "user_list":
                self.send({
                    "type": "websocket.send",
                    "text": self.encode_json({
                        "msg_type": "user_list",
                        "list": self.get_user_list(profile_id)
                    })
                })
            elif cmd_arg == "room_list":
                self.send({
                    "type": "websocket.send",
                    # "text": self.get_user_list(),
                    "text": self.encode_json({
                        "msg_type": "room_list",
                        "list": self.get_room_list()
                    })
                })

    def websocket_disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )
        pass

    def chatsignal(self, event):
        print("chatsignal TRIGERED")
        print(event['text'])
        print(event)
        self.send({
            # "type": "chatsignal",
            "type": "websocket.send",
            "text": event['text']
        })
