from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):

    def setUp(self):
        # this function will be executed whenever we run the test function
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        # we cannot use User.objects.creat()
        # because password need to be encrypted, username and email need to be normalized
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # each test function mush be start with 'test_' so that they can be used for test
        # all tests must use post not get
        response = self.client.get(LOGIN_URL, {
            'username' : self.user.username,
            'password' : 'correct password',
        })
        # login error, http status code return 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # use post but with wrong password
        response = self.client.post(LOGIN_URL, {
            'username' : self.user.username,
            'password' : 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # validate the status : not login yet
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # use the correct password
        response = self.client.post(LOGIN_URL, {
            'username' : self.user.username,
            'password' : 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        # validate the status : already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username' : self.user.username,
            'password' : 'correct password',
        })
        # check user already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test must use post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # use post logout successful
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # check the user already log out
        response =  self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username' : 'someone',
            'email' : 'someone@jiuzhang.com',
            'password' : 'any password',
        }
        # test get fail
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong email
        response = self.client.post(SIGNUP_URL, {
            'username' : 'someone',
            'email' : 'not a correct email',
            'password' : 'any password'
        })
        self.assertEqual(response.status_code, 400)

        # test short password
        response = self.client.post(SIGNUP_URL, {
            'username' : 'someone',
            'email' : 'someone@jiuzhang.com',
            'password' : '123',
        })
        self.assertEqual(response.status_code, 400)

        # test long username
        response = self.client.post(SIGNUP_URL, {
            'username' : 'username is tooooooooooooooo looooooooooooooong',
            'email' : 'someone@jiuzhang.com',
            'password' : 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # successfully login
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # validate user has already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)