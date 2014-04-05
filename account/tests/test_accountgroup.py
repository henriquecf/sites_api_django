# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from fixtures import user_accountuser_account_token_fixture
import routines
from account.models import AccountUser


class AccountUserAPITestCase(APILiveServerTestCase):
    model = AccountUser

    def setUp(self):
        self.url = reverse('accountgroup-list')
        self.data = {
            'role': 'Group'
        }
        self.altered_data = {
            'role': 'Group altered'
        }
        user_accountuser_account_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def alter_data(self, altered_data=False):
        if not altered_data:
            self.data.update({'role': 'Group {0}'.format(random.randint(1, 100000))})
        else:
            self.altered_data.update({'role': 'Group {0}'.format(random.randint(1, 100000))})

    def test_create(self):
        self.alter_data()
        response = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)

    def test_update(self):
        self.alter_data(altered_data=True)
        response = self.client.put(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    def test_partial_update(self):
        self.alter_data(altered_data=True)
        response = self.client.patch(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    def test_retrieve(self):
        response = self.client.get(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(1, response.data['count'])

    def test_destroy(self):
        response = self.client.delete(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_admin_permission(self):
        routines.test_admin_permission_routine(self)

    def test_resource_permission(self):
        routines.test_resource_permission_routine(self)

    def test_search_fields(self):
        fields = ['role']
        routines.test_search_fields_routine(self, search_fields=fields)

    def test_hyperlinked_fields(self):
        fields = ['account']
        routines.test_serializer_hyperlinked_fields_routine(self, fields=fields)

    def test_read_only_fields(self):
        fields = ['account', 'name']
        routines.test_serializer_read_only_fields_routine(self, fields=fields)

    def test_role_and_account_are_unique_together(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Should not be possible to create another account group with same role name')
        self.set_authorization_bearer(self.second_owner_token)
        response2 = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_201_CREATED, response2.status_code, response2.data)