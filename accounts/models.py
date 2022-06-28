from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    # One2One field will create an unique index to make sure one user will have only one user profile
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null = True)
    # It is not wise to use ImageField here, which will cause many problems
    # FileField is better, we always use url for files for visit
    avatar = models.FileField(null=True)
    # When an user is created, we will create a user profile object
    # sometime users are not decided about nickname, etc. so we set null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.user, self.nickname)

    def get_profile(user):
        if hasattr(user, '_cached_user_profile'):
            return getattr(user, '_cached_user_profile')
        profile, _ = UserProfile.objects.get_or_create(user=user)
        # user the attribute of user to do the cache, avoid repeat queires
        setattr(user, '_cached_user_profile', profile)
        return profile

    # add a property method for profile to visit it easier
    User.profile = property(get_profile)
