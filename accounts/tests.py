import datetime
from datetime import timedelta
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from resource.tests import APIGenericTest
from oauth2_provider.models import AccessToken, Application
from .models import Account


class AccountAPIGenericTest(APIGenericTest):

    def make_initial_data(self):
        User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
        owner = User.objects.create_user('owner', 'owner@owner.com', '123')
        owner.is_staff = True
        owner.save()
        second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
        second_owner.is_staff = True
        second_owner.save()
        owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
        owner_application = Application.objects.create(user=owner, client_type='confidential',
                                                       authorization_grant_type='password')
        second_owner_application = Application.objects.create(user=second_owner, client_type='confidential',
                                                              authorization_grant_type='password')
        self.owner_token = AccessToken.objects.create(user=owner, token=owner.username, application=owner_application,
                                                      expires=timezone.now() + timedelta(30)).token
        self.second_owner_token = AccessToken.objects.create(user=second_owner, token=second_owner.username,
                                                             application=second_owner_application,
                                                             expires=timezone.now() + timedelta(30)).token
        self.account_user_token = AccessToken.objects.create(user=owner_user, token=owner_user.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token


class AccountAPITestCase(APILiveServerTestCase):
    model = Account

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        self.account_api_generic_test = AccountAPIGenericTest(self)

    def test_create(self):
        self.account_api_generic_test.create(status_code=status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.account_api_generic_test.update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        self.account_api_generic_test.partial_update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        self.account_api_generic_test.retrieve()

    def test_list(self):
        self.account_api_generic_test.list()

    def test_destroy(self):
        self.account_api_generic_test.destroy()

    def test_admin_permission(self):
        self.account_api_generic_test.admin_permission()

    def test_hyperlinked_fields(self):
        accountuser_url = reverse('accountuser-list')
        response = self.client.post(accountuser_url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.account_api_generic_test.hyperlinked_fields(['owner'])

    def test_default_expiration_date(self):
        self.assertEqual(self.account_api_generic_test.first_object_response.data['expiration_date'],
                         datetime.date.today() + datetime.timedelta(30))

    def test_model_has_custom_permission(self):
        self.account_api_generic_test.model_has_custom_permission()