from .models import *
from rest_framework import serializers


# class ChatUserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = ChatUser
#         fields = ['id', 'username', 'avatar_image']
#
#
# class ChatRoomSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = ChatRoom
#         fields = ['id', 'name']
#
#
# class PersonalMessageSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = PersonalMessage
#         fields = ['id', 'sender', 'text', 'dest_user',]
#
#
# class RoomMessageSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = RoomMessage
#         fields = ['id', 'sender', 'text', 'dest_room',]
