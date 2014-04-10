# -*- coding: utf-8 -*-
import random
from copy import copy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from test_fixtures import user_accountuser_account_permissions_token_fixture
import test_routines


class UserAPITestCase(APILiveServerTestCase):
    model = User

    def setUp(self):
        self.url = reverse('user-list')
        self.data = {
            'username': 'user',
            'password': '123',
            'email': 'user@user.com'
        }
        self.altered_data = {
            'username': 'user-altered',
            'password': '123altered',
            'email': 'user-altered@user.com'
        }
        user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def alter_username(self, altered_data=False):
        username = 'user-{0}'.format(random.randint(1, 999999))
        if altered_data:
            data = self.altered_data
        else:
            data = self.data
        data.update({
            'username': username,
        })

    def test_api_basic_methods(self):
        self.alter_username()
        test_routines.test_api_basic_methods_routine(self, count=5)

    def test_resource_permission(self):
        self.alter_username()
        test_routines.test_resource_permission_routine(self)

    def test_required_email(self):
        data = copy(self.data)
        data.pop('email')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_search_fields(self):
        search_fields = ['username', 'email']
        for field in search_fields:
            filter_parameter = random.randint(1, 999999)
            self.altered_data.update(dict(username=filter_parameter + 1))
            if field == 'email':
                filter_parameter = '{0}@gm.com'.format(filter_parameter)
            self.altered_data.update({field: filter_parameter})
            self.client.post(self.url, self.altered_data)
            query_parameter = {'search': filter_parameter}
            response = self.client.get(self.url, query_parameter)
            self.assertEqual(response.data['count'], 1, 'Field "{0}" not in search fields'.format(field))

    def test_hashed_password(self):
        self.assertNotEqual(self.first_object_response.data['password'], self.data['password'])

    def test_excluded_serializer_fields(self):
        self.assertNotIn('is_superuser', self.first_object_response.data)
        response = self.client.get(self.first_object_response.data['url'])
        self.assertNotIn('password', response.data)

    def test_serializer_hyperlinked_fields(self):
        fields = ['accountuser', 'user_permissions', 'groups']
        test_routines.test_serializer_hyperlinked_fields_routine(self, fields=fields)

    def test_accountuser_created_has_same_account_as_request_user(self):
        account_user_url = self.first_object_response.data['accountuser']
        response = self.client.get(account_user_url)
        account_url = response.data['account']
        account_id = account_url.split('/')[-2]
        owner_account_id = User.objects.get(username=self.owner_token).accountuser.account.id
        self.assertEqual(account_id, str(owner_account_id))

    def test_serializer_read_only_fields(self):
        fields = ['accountuser', 'date_joined', 'last_login', 'is_active']
        test_routines.test_serializer_read_only_fields_routine(self, fields=fields)