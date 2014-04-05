# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from fixtures import user_account_token_fixture
import routines
from account.models import AccountUser


class AccountUserAPITestCase(APILiveServerTestCase):
    model = AccountUser

    def setUp(self):
        self.url = reverse('accountuser-list')
        self.data = {}
        self.altered_data = {}
        user_account_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_create(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

    def test_update(self):
        response = self.client.put(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

    def test_partial_update(self):
        response = self.client.patch(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

    def test_retrieve(self):
        response = self.client.get(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, self.first_object_response.data)

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])

    def test_destroy(self):
        response = self.client.delete(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_admin_permission(self):
        routines.test_admin_permission_routine(self)

    def test_accountuser_created_has_same_account_as_request_user(self):
        owner_user = User.objects.get(username=self.owner_token)
        url = self.first_object_response.data['account']
        account_id = url.split('/')[-2]
        self.assertEqual(account_id, str(owner_user.accountuser.account.id))

    def test_serializer_hyperlinked_fields(self):
        fields = ['user', 'account']
        routines.test_serializer_hyperlinked_fields_routine(self, fields=fields)

    def test_model_has_custom_permission(self):
        routines.test_model_has_custom_permission_routine(self)

    def test_serializer_read_only_fields(self):
        fields = ['user', 'account']
        routines.test_serializer_read_only_fields_routine(self, fields=fields)