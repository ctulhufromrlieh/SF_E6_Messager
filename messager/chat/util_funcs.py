from chat.models import Profile


def get_avatar_image_url(avatar_image):
    if bool(avatar_image):
        return avatar_image.url
    else:
        return ""


def get_profile_avatar_image_urls():
    profiles = Profile.objects.all()
    res = {}
    for currProfile in profiles:
        res[currProfile.id] = get_avatar_image_url(currProfile.avatar_image)

    return res
