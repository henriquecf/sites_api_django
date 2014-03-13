import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import Application, AccessToken
from account.models import Common


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


class AccountAPITestCase(APILiveServerTestCase):

    def oauth2_authorize(self, username, token, client_type='confidential', grant_type='password', is_superuser=False):
        email = '{0}@gmail.com'.format(username)
        if is_superuser:
            self.superuser = User.objects.create_superuser(username=username, email=email, password='123')
        else:
            self.superuser = User.objects.create(username=username, email=email, password='123')
        aplicacao = Application.objects.create(user=self.superuser, client_type=client_type, authorization_grant_type=grant_type, client_id=token)
        access_token = AccessToken.objects.create(user=self.superuser, token=token, application=aplicacao, expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {
            'username': 'user2',
            'password': '123',
        }
        self.oauth2_authorize(username='superuser', token='12345', is_superuser=True)
        super(AccountAPITestCase, self).setUp()

    def test_if_normal_user_can_not_list(self):
        self.oauth2_authorize('user', '123456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# TODO Create tests to create app user, test if just owner and children access data