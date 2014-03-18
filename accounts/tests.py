import copy
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application
from accounts.models import Common


class CommonTestCase(LiveServerTestCase):

    def setUp(self):
        self.common = Common.objects.create()

    def test_create_common_fields(self):
        """
        Ensure common is created
        """
        self.assertTrue(self.common.creation_date)
        self.assertTrue(self.common.last_modification_date)

    def test_update_common_fields(self):
        """
        Ensure common field last_modification_date is changed when object is saved
        """
        common2 = copy.copy(self.common)
        self.common.save()
        self.assertNotEqual(self.common.last_modification_date, common2.last_modification_date)


class UserTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='123', email='user@user.com')

    def test_if_user_create_url_exists(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_if_creates_user(self):
        users_count = User.objects.count()
        data = ({
            'username': 'henrique',
            'email': 'elo.henrique@gmail.com',
            'password1': '123',
            'password2': '123',
        })
        url = reverse('user-create')
        self.client.post(url, data)
        new_users_count = User.objects.count()
        self.assertEqual(users_count + 1, new_users_count, 'User was not created: {0}'.format(data))
        data.update({'username': 'ivan', 'email': ''})
        self.client.post(url, data)
        second_users_count = User.objects.count()
        self.assertEqual(new_users_count, second_users_count, 'User without email should not be created: {0}'.format(data))

    def test_if_user_can_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'user',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)


class AccountAPITestCase(APILiveServerTestCase):

    def oauth2_authorize(self, username, token, client_type='confidential', grant_type='password', superuser=False):
        email = '{0}@gmail.com'.format(username)
        if superuser:
            user = User.objects.create_superuser(username=username, email=email, password='123')
        else:
            user = User.objects.create_user(username=username, email=email, password='123')
        aplicacao = Application.objects.create(user=user, client_type=client_type, authorization_grant_type=grant_type, client_id=token)
        access_token = AccessToken.objects.create(user=user, token=token, application=aplicacao, expires=timezone.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {

        }
        self.oauth2_authorize('superuser', '12345', superuser=True)

    def test_if_can_not_access_create_account_without_login(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_any_user_can_access_data(self):
        self.oauth2_authorize('user', '123456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_if_creates_account(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# TODO Create tests to create app user, test if just owner and children access data