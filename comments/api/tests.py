from rest_framework.test import APIClient

from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu', 'linghui@jiuzhang.com')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.tweet = self.create_tweet(self.linghu)

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

