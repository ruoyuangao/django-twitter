from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import pre_delete, post_save

from accounts.listeners import user_changed, profile_changed

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

    # 定义一个 profile 的 property 方法，植入到 User 这个 model 里
    # 这样当我们通过 user 的一个实例化对象访问 profile 的时候，即 user_instance.profile
    # 就会在 UserProfile 中进行 get_or_create 来获得对应的 profile 的 object
    # 这种写法实际上是一个利用 Python 的灵活性进行 hack 的方法，这样会方便我们通过 user 快速
    # 访问到对应的 profile 信息。
    def get_profile(user):
        from accounts.services import UserService
        if hasattr(user, '_cached_user_profile'):
            return getattr(user, '_cached_user_profile')
        profile, _ = UserProfile.objects.get_or_create(user=user)
        # user the attribute of user to do the cache, avoid repeat queires
        setattr(user, '_cached_user_profile', profile)
        return profile

    # add a property method for profile to visit it easier
    User.profile = property(get_profile)

# hook up with listeners to invalidate cache
pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)
