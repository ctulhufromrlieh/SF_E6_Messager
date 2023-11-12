from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import F

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
    data = list(values)
    # print(data)
    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})


def get_chat_room_l(request):
    qs = ChatRoom.objects.all().values("id", "name")
    data = list(qs)
    # print(data)
    return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})

def select_chat(request, sel_type, sel_id):
    try:
        profile = request.user.profile
        profile.selected_category = sel_type
        profile.selected_chat = sel_id
        return HttpResponse(status=200)
    except:
        return HttpResponse(status=204)

    # return JsonResponse(data, safe=False)  # or JsonResponse({'data': data})

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