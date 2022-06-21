from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu', 'linghui@jiuzhang.com')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie', 'dongxie@jiuzhang.com')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # create followings and followers for dongxie
        for i in range(2):
            follower = self.create_user('dongxie_follower{}'.format(i), 'dongxie_follower{}@jiuzhang.com'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)
        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i), 'dongxie_following{}@jiuzhang.com'.format(i))
            Friendship.objects.create(from_user=self.dongxie, to_user=following)


    def test_follow(self):
        url = FOLLOW_URL.format(self.linghu.id)

        # we need to log in before follow
        response =  self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # we neet to use post for follow action
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        # we cannot follow ourselves
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        # successfully follow respond 201
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 201)

        # repeat follow, silent success
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # reverse follow will create new data
        count = Friendship.objects.count()
        response = self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.linghu.id)

        # we need to log in before unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # we neet to use post for unfollow action
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        # we cannot unfollow ourselves
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        # successfully unfollow respond 200
        Friendship.objects.create(from_user=self.dongxie, to_user=self.linghu)
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # unfollow when not following, silent success
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get followings return 200
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        # make sure the order is right
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'dongxie_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'dongxie_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'dongxie_following0',
        )


    def test_followers(self):
        url = FOLLOWERS_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        # make sure the order is right
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'dongxie_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'dongxie_follower0',
        )
