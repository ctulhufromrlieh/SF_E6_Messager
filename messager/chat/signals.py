from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from asgiref.sync import async_to_sync
import json
import channels.layers

from chat.consumers import ChatConsumer

from chat.models import Profile, ChatRoom, PersonalMessage, RoomMessage


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # print('create_user_profile')
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # print('save_user_profile')
    if hasattr(instance, 'profile'):
        instance.profile.save()

def base_profile_changed(sender, profile, **kwargs):
    if profile.id is None:
        msg_type = "profile_created"
        # msg_data= {
        #     "type": "chat.message",
        #     "text": json.dumps({
        #         "msg_type": "profile_created",
        #         "id": profile.id,
        #         "username": profile.user.username,
        #         # "avatar": profile.avatar_image
        #     })
        # }
    else:
        previous = Profile.objects.get(id=profile.id)
        # if (previous.avatar_image == profile.avatar_image) and (previous.user.username == profile.user.username):
        if (previous.user.username == profile.user.username):
            return
        else:
            msg_type = "profile_changed"

    msg_data = {
        "type": "chatsignal",
        "text": json.dumps({
            "msg_type": msg_type,
            "id": profile.id,
            "username": profile.user.username,
            # "avatar": profile.avatar_image
        })
    }

    channel_layer = channels.layers.get_channel_layer()
    # print(msg_data)
    async_to_sync(channel_layer.group_send)('events', msg_data)


@receiver(pre_save, sender=User)
def user_changed(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        base_profile_changed(sender, instance.profile, **kwargs)


@receiver(pre_save, sender=Profile)
def profile_changed(sender, instance, **kwargs):
    base_profile_changed(sender, instance, **kwargs)


@receiver(post_save, sender=PersonalMessage)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        channel_layer = channels.layers.get_channel_layer()
        ChatConsumer.send_personal_message(channel_layer, instance)


@receiver(post_save, sender=RoomMessage)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        channel_layer = channels.layers.get_channel_layer()
        ChatConsumer.send_room_message(channel_layer, instance)

        # dest_room_id = instance.dest_room.id
        # dest_user_ids = Profile.objects.filter(selected_category=1, selected_chat=dest_room_id).values_list('id', flat=True)
        #
        # # print(f"send_room_message to {dest_user_ids}")
        #
        # for curr_dest_user_id in dest_user_ids:
        #     print(f"send_room_message to {curr_dest_user_id}")
        #     # curr_group_name = ChatConsumer.get_single_group_for_profile(curr_dest_user_id)
        #     # print(f"send_room_message in {curr_group_name}")
        #     # data = {
        #     #     "valid": True,
        #     #     "messages": []
        #     # }
        #
        #     msg_data = {
        #           # "type": "websocket.send",
        #           "type": "chatsignal",
        #           "text": json.dumps({
        #               "msg_type": "message_created",
        #               "username": instance.sender.user.username,
        #               "sender_id": instance.sender.id,
        #               "text": instance.text
        #           })
        #         }
        #     print(msg_data)
        #
        #     channel_layer = channels.layers.get_channel_layer()
        #     async_to_sync(channel_layer.group_send('events', msg_data))
        #     # async_to_sync(
        #     #     # channel_layer.group_send(curr_group_name, msg)
        #     #     channel_layer.group_send('events', msg_data)
        #     # )
