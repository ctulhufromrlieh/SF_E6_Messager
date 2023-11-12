from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from asgiref.sync import async_to_sync
import json
import channels.layers

from chat.models import Profile, ChatRoom


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
            # msg_data = {
            #     "type": "chat.message",
            #     "text": json.dumps({
            #         "msg_type": "profile_changed",
            #         "id": profile.id,
            #         "username": profile.user.username,
            #         # "avatar": profile.avatar_image
            #     })
            # }

    msg_data = {
        "type": "chatsignal",
        "text": json.dumps({
            "msg_type": msg_type,
            "id": profile.id,
            "username": profile.user.username,
            # "avatar": profile.avatar_image
        })
    }
    # msg_data = {
    #     "type": "chatsignal",
    #     "text": "123"
    # }

    msg_text = json.dumps(msg_data)
    # print(msg_data)
    # print(msg_text)
    channel_layer = channels.layers.get_channel_layer()
    # async_to_sync(channel_layer.send)('events', msg_text)
    print(msg_data)
    # ch_group_list = channel_layer.group_channels('events')
    # ch_group_list = channel_layer['events']
    # print(ch_group_list)
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
