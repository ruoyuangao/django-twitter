from rest_framework.test import APIClient
from comments.models import Comment
from django.utils import timezone
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu', 'linghui@jiuzhang.com')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.tweet = self.create_tweet(self.linghu)

        self.dongxie = self.create_user('dongxie', 'dongxie@jiuzhang.com')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

    def test_create(self):
        # must create after login
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)
        # cannot create without parameters
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        # cannot create without content
        response = self.linghu_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)
        # cannot create without tweet_id
        response = self.linghu_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        # the content cannot be too long
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)
        # success create with tweet_id and proper content
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_update(self):
        comment = self.create_comment(self.linghu, self.tweet, 'original')
        another_tweet = self.create_tweet(self.dongxie)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # when we use put, we cannot update without login
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # when we use put, we cannot update other's comment
        response = self.dongxie_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # we cannot update data other than content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(url, {
            'content': 'new',
            'user_id': self.dongxie.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)
