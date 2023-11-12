from django.db import models
from django.contrib.auth.models import User
from django.db.models import TextField, DateField, CharField


class Profile(models.Model):
    sel_cat_types = [("NONE", "None"), ("USER", "User"), ("ROOM", "Room")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_image = models.ImageField(upload_to='uploads/')
    selected_category = models.CharField(max_length=4, choices=sel_cat_types, default="NONE")
    selected_chat = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.pk}: {self.user.username}"


# class ChatUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar_image = models.ImageField(upload_to='uploads/')


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)


class PersonalMessage(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender_personal_messages")
    text = TextField(default="")
    creation_date = models.DateTimeField(auto_now_add=True)
    dest_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="dest_user_personal_messages")


class RoomMessage(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = TextField(default="")
    creation_date = models.DateTimeField(auto_now_add=True)
    dest_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
