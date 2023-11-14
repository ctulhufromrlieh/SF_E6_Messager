from channels.consumer import AsyncConsumer, SyncConsumer
import json
from django.db.models import F
from asgiref.sync import async_to_sync

from chat.models import Profile, ChatRoom, PersonalMessage, RoomMessage
# from chat.util_funcs import get_avatar_image_url


class ChatConsumer(SyncConsumer):
    @classmethod
    def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content)

    @classmethod
    def get_input_data(cls, text_data):
        if 'text' not in text_data:
            return

        data = cls.decode_json(text_data['text'])
        if 'get' in data:
            # print('get in data')
            return 'get', data['get'], data
        elif 'post' in data:
            return 'post', data['post'], data

    @classmethod
    def get_profile_id_by_user_id(cls, user_id):
        return Profile.objects.get(user__id=user_id).id

    # unused
    def get_user_list(self, my_profile_id):
        qs = Profile.objects.all()
        qs = qs.exclude(id=my_profile_id)
        values = qs.annotate(username=F('user__username')).values("id", "username", )
        lst = list(values)
        return lst;

    # unused
    def get_room_list(self):
        qs = ChatRoom.objects.all()
        values = qs.values("id", "name", )
        lst = list(values)
        return lst;

    def receive_message(self, profile_id, msg_text):
        profile = Profile.objects.get(id=profile_id)
        # print(f"receive_message: {profile_id}, {msg_text}, profile.selected_category={profile.selected_category}")
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
            "type": "chatsignal",
            "text": cls.encode_json({
                "msg_type": "message_created",
                "username": pm.sender.user.username,
                "sender_id": pm.sender.id,
                # "avatar_image_url": get_avatar_image_url(pm.sender.avatar_image),
                "avatar_image_url": pm.sender.avatar_image_url,
                "text": pm.text
            })
        }

        async_to_sync(channel_layer.group_send)(group_name_sender, msg_data)

        dest_profile = Profile.objects.get(id=dest_id)
        print(f"profile {dest_id} used selected_chat={dest_profile.selected_chat}")
        if (dest_profile.selected_category == 0) and (dest_profile.selected_chat == sender_id):
            async_to_sync(channel_layer.group_send)(group_name_dest, msg_data)

    @classmethod
    def send_room_message(cls, channel_layer, rm):
        print(channel_layer)
        dest_room_id = rm.dest_room.id
        dest_user_ids = Profile.objects.filter(selected_category=1, selected_chat=dest_room_id).values_list('id',
                                                                                                            flat=True)

        for curr_dest_user_id in dest_user_ids:
            curr_group_name = cls.get_single_group_for_profile(curr_dest_user_id)

            msg_data = {
                "type": "chatsignal",
                "text": cls.encode_json({
                    "msg_type": "message_created",
                    "username": rm.sender.user.username,
                    "sender_id": rm.sender.id,
                    # "avatar_image_url": get_avatar_image_url(rm.sender.avatar_image),
                    "avatar_image_url": rm.sender.avatar_image_url,
                    "text": rm.text
                })
            }

            async_to_sync(channel_layer.group_send)(curr_group_name, msg_data)

    @classmethod
    def base_profile_changed(cls, channel_layer, sender, profile, created, **kwargs):
        if created or (profile.id is None):
            msg_type = "profile_created"
        else:
            previous = Profile.objects.get(id=profile.id)
            # if (previous.avatar_image == profile.avatar_image) and (previous.user.username == profile.user.username):
            # if (previous.user.username == profile.user.username) \
            #         and (get_avatar_image_url(previous.avatar_image) == get_avatar_image_url(profile.avatar_image)):
            # if (previous.user.username == profile.user.username) \
            #         and (previous.avatar_image_url == profile.avatar_image_url):
            #     return
            # else:
            #     msg_type = "profile_changed"
            msg_type = "profile_changed"

        msg_data = {
            "type": "chatsignal",
            "text": json.dumps({
                "msg_type": msg_type,
                "id": profile.id,
                "username": profile.user.username,
                # "avatar_image_url": get_avatar_image_url(profile.avatar_image)
                "avatar_image_url": profile.avatar_image_url
            })
        }

        async_to_sync(channel_layer.group_send)('events', msg_data)

    @classmethod
    def get_single_group_for_profile(self, profile_id):
        return f"single_user_group_{profile_id}"

    def websocket_connect(self, event):
        async_to_sync(self.channel_layer.group_add)("events", self.channel_name)

        profile_id = self.scope['user'].profile.id
        single_group_name = self.get_single_group_for_profile(profile_id)
        async_to_sync(self.channel_layer.group_add)(single_group_name, self.channel_name)

        # # set to unselected state
        # profile = self.scope['user'].profile
        # profile.selected_category = -1
        # profile.selected_chat = -1

        self.send({"type": "websocket.accept"})

    def websocket_receive(self, text_data):
        # print(text_data)
        cmd_type, cmd_arg, data = self.get_input_data(text_data)

        user = self.scope['user']
        profile_id = self.get_profile_id_by_user_id(user.id)
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
