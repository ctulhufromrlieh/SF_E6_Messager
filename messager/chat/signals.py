from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from asgiref.sync import async_to_sync
import json
import channels.layers

from chat.consumers import ChatConsumer

from chat.models import Profile, ChatRoom, PersonalMessage, RoomMessage
from chat.util_funcs import get_avatar_image_url


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


def base_profile_changed(sender, profile, created, **kwargs):
    if created or (profile.id is None):
        msg_type = "profile_created"
    else:
        previous = Profile.objects.get(id=profile.id)
        # if (previous.avatar_image == profile.avatar_image) and (previous.user.username == profile.user.username):
        if (previous.user.username == profile.user.username) \
                and (get_avatar_image_url(previous.avatar_image) == get_avatar_image_url(profile.avatar_image)):
            return
        else:
            msg_type = "profile_changed"

    msg_data = {
        "type": "chatsignal",
        "text": json.dumps({
            "msg_type": msg_type,
            "id": profile.id,
            "username": profile.user.username,
            "avatar_image_url": get_avatar_image_url(profile.avatar_image)
            # "avatar": profile.avatar_image
        })
    }

    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)('events', msg_data)


@receiver(pre_save, sender=User)
def user_changed(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        base_profile_changed(sender, instance.profile, None, **kwargs)


# @receiver(pre_save, sender=Profile)
# def pre_profile_changed(sender, instance, **kwargs):
#     base_profile_changed(sender, instance, None, **kwargs)

@receiver(post_save, sender=Profile)
def post_profile_changed(sender, instance, created, **kwargs):
    # print("post_profile_changed")
    # print(sender, instance, created)
    base_profile_changed(sender, instance, created, **kwargs)

@receiver(post_save, sender=ChatRoom)
def create_chat_room(sender, instance, created, **kwargs):
    channel_layer = channels.layers.get_channel_layer()
    if created:
        ChatConsumer.create_chat_room(channel_layer, instance)
    else:
        ChatConsumer.change_chat_room(channel_layer, instance)


@receiver(pre_delete, sender=ChatRoom)
def log_deleted_question(sender, instance, using, **kwargs):
    channel_layer = channels.layers.get_channel_layer()
    ChatConsumer.delete_chat_room(channel_layer, instance)


@receiver(post_save, sender=PersonalMessage)
def create_personal_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = channels.layers.get_channel_layer()
        ChatConsumer.send_personal_message(channel_layer, instance)


@receiver(post_save, sender=RoomMessage)
def create_room_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = channels.layers.get_channel_layer()
        ChatConsumer.send_room_message(channel_layer, instance)

