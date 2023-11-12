from channels.consumer import AsyncConsumer, SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from django.core import serializers
# from channels.auth import channel_session_user_from_http
# from channels import Group
import json
from django.db.models import F
from asgiref.sync import async_to_sync

from chat.models import Profile, ChatRoom, PersonalMessage, RoomMessage


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
            return 'get', data['get'], data
        elif 'post' in data:
            return 'post', data['post'], data

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

    # def get_profiles_for_message(self):

    def receive_message(self, profile_id, msg_text):
        profile = Profile.objects.get(id=profile_id)
        print(f"receive_message: {profile_id}, {msg_text}, profile.selected_category={profile.selected_category}")
        if profile.selected_category == 0:
            dest = Profile.objects.get(id=profile.selected_chat)
            PersonalMessage.objects.create(sender=profile, text=msg_text, dest_user=dest)
        elif profile.selected_category == 1:
            dest = ChatRoom.objects.get(id=profile.selected_chat)
            RoomMessage.objects.create(sender=profile, text=msg_text, dest_room=dest)

    @classmethod
    def create_chat_room(cls, channel_layer, cr):
        msg_data = {
            "type": "chatsignal",
            "text": cls.encode_json({
                "msg_type": "chatroom_created",
                "id": cr.id,
                "name": cr.name,
                "owner_id": cr.owner.id,
            })
        }

        async_to_sync(channel_layer.group_send)('events', msg_data)

    @classmethod
    def change_chat_room(cls, channel_layer, cr):
        msg_data = {
            "type": "chatsignal",
            "text": cls.encode_json({
                "msg_type": "chatroom_changed",
                "id": cr.id,
                "name": cr.name,
                "owner_id": cr.owner.id,
            })
        }

        async_to_sync(channel_layer.group_send)('events', msg_data)

    @classmethod
    def delete_chat_room(cls, channel_layer, cr):
        msg_data = {
            "type": "chatsignal",
            "text": cls.encode_json({
                "msg_type": "chatroom_deleted",
                "id": cr.id,
                "name": cr.name,
                "owner_id": cr.owner.id,
            })
        }

        async_to_sync(channel_layer.group_send)('events', msg_data)

    @classmethod
    def send_personal_message(cls, channel_layer, pm):
        sender_id = pm.sender.id
        group_name_sender = cls.get_single_group_for_profile(sender_id)

        dest_id = pm.dest_user.id
        group_name_dest = cls.get_single_group_for_profile(dest_id)

        msg_data = {
            # "type": "websocket.send",
            "type": "chatsignal",
            "text": cls.encode_json({
                "msg_type": "message_created",
                "username": pm.sender.user.username,
                "sender_id": pm.sender.id,
                "text": pm.text
            })
        }

        async_to_sync(channel_layer.group_send)(group_name_sender, msg_data)
        async_to_sync(channel_layer.group_send)(group_name_dest, msg_data)

    @classmethod
    def send_room_message(cls, channel_layer, rm):
        print(channel_layer)
        dest_room_id = rm.dest_room.id
        dest_user_ids = Profile.objects.filter(selected_category=1, selected_chat=dest_room_id).values_list('id', flat=True)

        # print(f"send_room_message to {dest_user_ids}")

        for curr_dest_user_id in dest_user_ids:
            print(f"send_room_message to {curr_dest_user_id}")
            curr_group_name = cls.get_single_group_for_profile(curr_dest_user_id)
            print(f"send_room_message in {curr_group_name}")
            # data = {
            #     "valid": True,
            #     "messages": []
            # }

            msg_data = {
                  # "type": "websocket.send",
                  "type": "chatsignal",
                  "text": cls.encode_json({
                      "msg_type": "message_created",
                      "username": rm.sender.user.username,
                      "sender_id": rm.sender.id,
                      "text": rm.text
                  })
                }
            print(msg_data)

            async_to_sync(channel_layer.group_send)(curr_group_name, msg_data)

    @classmethod
    def get_single_group_for_profile(self, profile_id):
        return f"single_user_group_{profile_id}"

    def websocket_connect(self, event):
        async_to_sync(self.channel_layer.group_add)("events", self.channel_name)

        profile_id = self.scope['user'].profile.id
        single_group_name = self.get_single_group_for_profile(profile_id)
        async_to_sync(self.channel_layer.group_add)(single_group_name, self.channel_name)
        print(f"Group {single_group_name} created!")

        # await self.send({"type": "websocket.accept"})
        self.send({"type": "websocket.accept"})

    def websocket_receive(self, text_data):
        # print(text_data)
        cmd_type, cmd_arg, data = self.get_input_data(text_data)

        user = self.scope['user']
        profile_id = self.get_profile_id_by_user_id(user.id)
        print(f"user.id = {user.id}")
        print(f"profile.id = {self.get_profile_id_by_user_id(user.id)}")
        if not user.is_authenticated:
            return

        if cmd_type == "get":
            # unused now
            if cmd_arg == "user_list":
                self.send({
                    "type": "websocket.send",
                    "text": self.encode_json({
                        "msg_type": "user_list",
                        "list": self.get_user_list(profile_id)
                    })
                })
            # unused now
            elif cmd_arg == "room_list":
                self.send({
                    "type": "websocket.send",
                    # "text": self.get_user_list(),
                    "text": self.encode_json({
                        "msg_type": "room_list",
                        "list": self.get_room_list()
                    })
                })
        elif cmd_type == "post":
            if cmd_arg == "send_message":
                print(data)
                self.receive_message(profile_id, data['text'])


    def websocket_disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )

        profile_id = self.scope['user'].profile.id
        single_group_name = self.get_single_group_for_profile(profile_id)
        async_to_sync(self.channel_layer.group_discard)(
            single_group_name,
            self.channel_name
        )
        # pass

    def chatsignal(self, event):
        print("chatsignal TRIGERED")
        # print(event['text'])
        # print(event)
        self.send({
            # "type": "chatsignal",
            "type": "websocket.send",
            "text": event['text']
        })
