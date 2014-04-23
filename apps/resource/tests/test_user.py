# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase

from test_fixtures import user_accountuser_account_permissions_token_fixture
import test_routines


class UserAPITestCase(APILiveServerTestCase):
    model = User

    def setUp(self):
        self.url = reverse('user-list')
        self.data = {
            'user': {
                'username': 'other_user',
                'password': '123',
                'email': 'otheruser@otheruser.com',
            }
        }
        self.altered_data = {
            'user': {
                'username': 'other_user_altered',
                'password': '123',
                'email': 'otheruseraltered@teste.com',
            }
        }
        user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def alter_data(self, altered_data=False):
        username = 'user-{0}'.format(random.randint(1, 999999))
        email = '{0}@teste.com'.format(username)
        if not altered_data:
            data = self.data
        else:
            data = self.altered_data
        data.update({'user': {'username': username, 'email': email, 'password': '123'}})

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self, alter_data=True, count=2)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self, alter_data=True)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self, alter_data=True)

    def test_accountuser_created_has_same_account_as_request_user(self):
        owner_user = User.objects.get(username=self.owner_token)
        account_id = self.first_object_response.data['owner']['id']
        self.assertEqual(account_id, owner_user.user.owner.id)

    def test_serializer_hyperlinked_fields(self):
        fields = []
        test_routines.test_serializer_hyperlinked_fields_routine(self, fields=fields)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_serializer_read_only_fields(self):
        fields = []
        test_routines.test_serializer_read_only_fields_routine(self, fields=fields)

    def test_excluded_fields(self):
        excluded_fields = ['is_superuser', 'is_staff']
        for field in excluded_fields:
            self.assertNotIn(field, self.first_object_response.data['user'])