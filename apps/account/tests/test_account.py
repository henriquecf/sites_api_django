# -*- coding: utf-8 -*-
import datetime
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from test_fixtures import user_token_fixture
import test_routines
from apps.account.models import Account


class AccountAPITestCase(APILiveServerTestCase):
    model = Account

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        user_token_fixture(self)
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
        test_routines.test_admin_permission_routine(self)

    def test_serializer_hyperlinked_fields(self):
        accountuser_url = reverse('accountuser-list')
        response = self.client.post(accountuser_url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        fields = ['owner']
        test_routines.test_serializer_hyperlinked_fields_routine(self, fields)

    def test_default_expiration_date(self):
        self.assertEqual(self.first_object_response.data['expiration_date'],
                         datetime.date.today() + datetime.timedelta(30))

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_serializer_read_only_fields(self):
        fields = ['owner']
        test_routines.test_serializer_read_only_fields_routine(self, fields)