from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt

from .models import *

from .models import Profile
from .forms import UploadImageForm
from chat.util_funcs import get_profile_avatar_image_urls


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
    # values = qs.annotate(username=F('user__username')).values("id", "username", )
    qs = qs.annotate(username=F('user__username'))
    values = qs.values("id", "username", )
    lst = list(values)
    for curr_user in lst:
        curr_avatar_image = Profile.objects.get(id=curr_user["id"]).avatar_image
        if bool(curr_avatar_image):
            curr_user["avatar_image_url"] = curr_avatar_image.url
        else:
            curr_user["avatar_image_url"] = ""

    print(lst)


    # if bool(request.user.profile.avatar_image):
    #     my_avatar_url = request.user.profile.avatar_image.url
    # else:
    #     my_avatar_url = ""
    # my_avatar_url = get_avatar_image_url(request.user.profile.avatar_image)
    my_avatar_url = request.user.profile.avatar_image_url
    data = {
        "list": list(values),
        "me": {
            "id": request.user.profile.id,
            "username": request.user.profile.user.username,
            "avatar_image_url": my_avatar_url,
            "sel_cat": request.user.profile.selected_category,
            "sel_chat": request.user.profile.selected_chat,
        }
    }
    return JsonResponse(data, safe=False)


def get_chat_room_l(request):
    qs = ChatRoom.objects.all()
    values = qs.values("id", "name", "owner_id")
    data = list(values)

    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})


def get_messages_for_profile(profile):
    sel_cat = profile.selected_category
    sel_chat = profile.selected_chat

    if sel_cat == 0:
        criterion1 = Q(dest_user=sel_chat)
        criterion2 = Q(sender__id=sel_chat)
        qs = PersonalMessage.objects.filter(criterion1 | criterion2).order_by("creation_date")
        qs = qs.annotate(username=F('sender__user__username'))

        values = qs.values("id", "sender_id", "text", "username")
        data = list(values)
        return data
    elif sel_cat == 1:
        qs = RoomMessage.objects.filter(dest_room=sel_chat).order_by("creation_date")
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

        messages = get_messages_for_profile(profile)
        profile_avatar_image_urls = get_profile_avatar_image_urls()
        for curr_message in messages:
            curr_message["avatar_image_url"] = profile_avatar_image_urls[curr_message["sender_id"]]

        data = {
            "valid": len(messages) > 0,
            "messages": messages
        }
        # print(data)
        return JsonResponse(data, status=200)
    except:
        return JsonResponse({}, status=204)


@csrf_exempt
def set_user_data(request):
    try:
        profile = request.user.profile

        new_username = request.POST['username']
        if new_username:
            profile.user.username = new_username
            profile.user.save()

        avatar_image = request.FILES.get('avatar_image', None)
        if avatar_image:
            profile.avatar_image = avatar_image
        else:
            profile.avatar_image = None
        profile.save()

        data = {
            "username": profile.user.username,
            # "avatar_image_url": get_avatar_image_url(profile.avatar_image)
            "avatar_image_url": profile.avatar_image_url
        }

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