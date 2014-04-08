# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from test_fixtures import user_accountuser_account_token_fixture
import test_routines
from account.models import FilterRestriction


class FilterPermissionAPITestCase(APILiveServerTestCase):
    model = FilterRestriction

    def setUp(self):
        self.url = reverse('filterrestriction-list')
        user_accountuser_account_token_fixture(self)
        self.data = {
            'filter_field': 'creator',
            'values': '1',
            'accountuser': self.owner.accountuser.id,
            'permission': Permission.objects.first().id,
        }
        self.altered_data = {
            'filter_field': 'owner',
            'values': '1',
            'accountuser': self.owner.accountuser.id,
            'permission': Permission.objects.first().id,
        }
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def alter_data(self, accountuser_id, altered_data=False):
        if not altered_data:
            data = self.data
        else:
            data = self.altered_data
        filter_field = 'filter-field-{0}'.format(random.randint(1, 99999))
        data.update({
            'filter_field': filter_field,
            'values': '1',
            'accountuser': accountuser_id,
            'permission': Permission.objects.first().id,
        })

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_second_owner_permission(self):
        self.set_authorization_bearer(self.second_owner_token)

        response = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

        response2 = self.client.put(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response2.status_code, response2.data)

        response3 = self.client.patch(self.first_object_response.data['url'], self.altered_data)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response3.status_code, response3.data)

        response4 = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response4.status_code, response4.data)
        self.assertEqual(0, response4.data['count'], response4.data)

        response5 = self.client.get(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_404_NOT_FOUND, response5.status_code, response5.data)

        response6 = self.client.delete(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_404_NOT_FOUND, response6.status_code, response6.data)

    def test_second_owner_basic_api_methods(self):
        self.set_authorization_bearer(self.second_owner_token)
        self.alter_data(self.second_owner.accountuser.id)
        self.alter_data(self.second_owner.accountuser.id, altered_data=True)
        response = self.client.post(self.url, self.data)
        test_routines.test_api_basic_methods_routine(self, token=self.second_owner_token,
                                                     object_url=response.data['url'])

    def test_permission_is_assigned_to_user(self):
        permission = Permission.objects.get(id=self.data['permission'])
        self.assertIn(permission, self.owner.user_permissions.all())

    def test_permission_is_unassigned_when_filter_is_deleted(self):
        self.client.delete(self.first_object_response.data['url'])
        permission = Permission.objects.get(id=self.data['permission'])
        self.assertNotIn(permission, self.owner.user_permissions.all())