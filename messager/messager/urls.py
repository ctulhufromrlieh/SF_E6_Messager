"""
URL configuration for messager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
# from rest_framework import routers
# from rest_framework_swagger.views import get_swagger_view
from chat.views import *


# router = routers.DefaultRouter()
# router.register(r'chat_users', ChatUserViewset)
# router.register(r'chat_rooms', ChatRoomViewset)
# router.register(r'personal_messages', PersonalMessageViewset, 'personal_message')
# router.register(r'room_messages', RoomMessageViewset, 'room_message')


# schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # path('swagger/', schema_view),
    path('chat/', login_required(TemplateView.as_view(template_name="chat_main.html"))),
    path('upload_image/', upload_image, name='upload_image'),
    path('', RedirectView.as_view(url='chat/', permanent=False), name='index'),
    path('chat_users/get_list/', get_chat_user_l),
    path('chat_rooms/get_list/', get_chat_room_l),
    path('chat_rooms/create/<str:name>/', create_chat_room),
    path('chat_rooms/change/<int:id>/<str:name>/', change_chat_room),
    path('chat_rooms/delete/<int:id>/', delete_chat_room),
    path('chat_select/<int:sel_cat>/<int:sel_chat>/', select_chat),
    path('chat/set_user_data/', set_user_data),
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
