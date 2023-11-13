from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import F, Q

from rest_framework import viewsets
from rest_framework import permissions

from .serializers import *
from .models import *

# from .models import ChatUser
from .models import Profile
from .forms import UploadImageForm


def upload_image(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = UploadImageForm()
    profiles = Profile.objects.all()
    return render(request, 'upload_image.html', {'form': form, 'chat_users': profiles})


def get_chat_user_l(request):
    # qs = Profile.objects.all().exclude(id=request.user.profile.id).values("id", "user__username")
    qs = Profile.objects.all().exclude(id=request.user.profile.id)
    # values = qs.values("id", "user__username")
    values = qs.annotate(username=F('user__username')).values("id", "username", )
    # data = list(values)
    data = {
        "list": list(values),
        "me": {
            "id": request.user.profile.id,
            "username": request.user.profile.user.username
        }
    }
    # print(data)
    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})


def get_chat_room_l(request):
    # qs = ChatRoom.objects.all().values("id", "name")
    qs = ChatRoom.objects.all()
    # qs = qs.annotate(owner_id=F('owner__id'))
    values = ChatRoom.objects.all().values("id", "name", "owner_id")
    data = list(values)
    # print(data)
    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})


def get_messages_for_profile(profile):
    sel_cat = profile.selected_category
    sel_chat = profile.selected_chat

    print(f"get_messages_for_profile - start, {sel_cat}, {sel_chat}")

    if sel_cat == 0:
        # qs = PersonalMessage.objects.filter(dest_user=sel_chat)

        criterion1 = Q(dest_user=sel_chat)
        criterion2 = Q(sender__id=sel_chat)
        qs = PersonalMessage.objects.filter(criterion1 | criterion2).order_by("creation_date")
        print("get_messages_for_profile: sel_cat == 0: before annotate")
        # qs = qs.annotate(sender_id=F("sender__id")).anotate(username=F('sender__user__username'))
        qs = qs.annotate(username=F('sender__user__username'))
        print("get_messages_for_profile: sel_cat == 0: after annotate")
        values = qs.values("id", "sender_id", "text", "username")
        data = list(values)
        # print("get_messages_for_profile:")
        # print(data)
        return data
    elif sel_cat == 1:
        print("get_messages_for_profile: sel_cat == 1")
        qs = RoomMessage.objects.filter(dest_room=sel_chat).order_by("creation_date")
        print("get_messages_for_profile: sel_cat == 1: before annotate")
        # qs = qs.annotate(sender_id=F("sender__id")).annotate(username=F('sender__user__username'))
        qs = qs.annotate(username=F('sender__user__username'))

        values = qs.values("id", "sender_id", "text", "username")
        data = list(values)
        return data
    else:
        return []


def select_chat(request, sel_cat, sel_chat):
    try:
        profile = request.user.profile
        profile.selected_category = sel_cat
        profile.selected_chat = sel_chat
        profile.save()
        # print(f"select_chat {sel_cat} | {sel_chat}")
        # print("before get_messages_for_profile")
        messages = get_messages_for_profile(profile)
        data = {
            "valid": len(messages) > 0,
            "messages": messages
        }
        # print(data)
        return JsonResponse(data, status=200)
    except:
        return JsonResponse({}, status=204)

def create_chat_room(request, name):
    chatroom = ChatRoom.objects.create(name=name, owner=request.user.profile)
    data = {
        "id": chatroom.id,
        "name": chatroom.name,
        "owner_id": chatroom.owner.id
    }
    return JsonResponse(data, status=201)


def change_chat_room(request, id, name):
    chatroom = ChatRoom.objects.get(pk=id)
    print(f"change_chat_room, owner_id={chatroom.owner.id}, profile_id={request.user.profile.id}")
    if chatroom.owner.id == request.user.profile.id:
        chatroom.name = name
        chatroom.save()
        data = {
            "id": chatroom.id,
            "name": chatroom.name,
            "owner_id": chatroom.owner.id
        }

        return JsonResponse(data, status=200)
    else:
        return JsonResponse({}, status=403)

def delete_chat_room(request, id):
    chatroom = ChatRoom.objects.get(pk=id)
    if chatroom.owner.id == request.user.profile.id:
        data = {
            "id": chatroom.id,
            "name": chatroom.name,
            "owner_id": chatroom.owner.id
        }
        chatroom.delete()

        return JsonResponse(data, status=200)
    else:
        return JsonResponse({}, status=403)

# class ChatUserViewset(viewsets.ModelViewSet):
#     queryset = ChatUser.objects.all()
#     serializer_class = ChatUserSerializer
#
#
# class ChatRoomViewset(viewsets.ModelViewSet):
#     queryset = ChatRoom.objects.all()
#     serializer_class = ChatRoomSerializer
#
#
# class PersonalMessageViewset(viewsets.ModelViewSet):
#     # queryset = PersonalMessage.objects.all()
#     serializer_class = PersonalMessageSerializer
#
#     def get_queryset(self):
#         return PersonalMessage.objects.all()
#
#
# class RoomMessageViewset(viewsets.ModelViewSet):
#     # queryset = RoomMessage.objects.all()
#     serializer_class = RoomMessageSerializer
#
#     def get_queryset(self):
#         return RoomMessage.objects.all()