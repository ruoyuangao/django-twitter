from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User

from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet

class TestCase(DjangoTestCase):

    def create_user(self, username, email, password=None):
        if password is None:
            password = 'generic password'
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance