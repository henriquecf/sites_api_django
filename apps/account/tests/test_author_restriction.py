# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from apps.resource.models import Group as CustomGroup, User as CustomUser

from test_fixtures import user_accountuser_account_token_fixture
import test_routines
from apps.account.models import AuthorRestriction, User, Group
from apps.account.serializers import AuthorRestrictionSerializer


class AuthorRestrictionAPITestCase(APILiveServerTestCase):
    model = AuthorRestriction

    def setUp(self):
        self.url = reverse('authorrestriction-list')
        user_accountuser_account_token_fixture(self)
        self.data = {
            'filter_values': '1',
            'user': self.owner.id,
            'permission': Permission.objects.first().id,
        }
        self.altered_data = {
            'filter_values': '1',
            'user': self.owner.id,
            'permission': Permission.objects.first().id,
        }
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def alter_data(self, user_id, altered_data=False):
        if not altered_data:
            data = self.data
        else:
            data = self.altered_data
        filter_field = 'filter-field-{0}'.format(random.randint(1, 99999))
        data.update({
            'filter_field': filter_field,
            'filter_values': '1',
            'user': user_id,
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
        self.alter_data(self.second_owner.id)
        self.alter_data(self.second_owner.id, altered_data=True)
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

    def test_filter_permission_with_accountgroup(self):
        self.data.pop('user')
        accountgroup = CustomGroup.objects.create(role='Test role', account=self.owner.user.account,
                                                  author=self.owner)
        self.data.update({'group': accountgroup.group.id})
        test_routines.test_api_basic_methods_routine(self)

    def test_permission_is_assigned_and_unassigned_to_group(self):
        self.data.pop('user')
        accountgroup = CustomGroup.objects.create(role='Test role', account=self.owner.user.account,
                                                  author=self.owner)
        self.data.update({'group': accountgroup.group.id})
        response3 = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_201_CREATED, response3.status_code, response3.data)

        permission = Permission.objects.get(id=self.data['permission'])

        self.assertIn(permission, accountgroup.group.permissions.all(), accountgroup.group)

        response2 = self.client.delete(response3.data['url'])
        self.assertEqual(status.HTTP_204_NO_CONTENT, response2.status_code, response2.data)
        self.assertNotIn(permission, accountgroup.group.permissions.all())

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_user_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        user = self.account_user
        possible_users = AuthorRestrictionSerializer(context={'request': request}).get_fields()['user'].queryset
        self.assertIn(user, possible_users)

        other_account_user = User.objects.create_user(username='other_user', password='123')
        CustomUser.objects.create(user=other_account_user, account=self.second_owner.account, author=self.second_owner)

        possible_users = AuthorRestrictionSerializer(context={'request': request}).get_fields()['user'].queryset
        self.assertIn(user, possible_users)
        self.assertNotIn(other_account_user, possible_users)

        request.user = self.second_owner
        possible_users = AuthorRestrictionSerializer(context={'request': request}).get_fields()['user'].queryset
        self.assertNotIn(user, possible_users)
        self.assertIn(other_account_user, possible_users)

    def test_group_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        accountgroup = CustomGroup.objects.create(role='group', account=self.owner.account, author=self.owner)

        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertIn(accountgroup.group, possible_groups)

        other_account_group = CustomGroup.objects.create(role='other_group', account=self.second_owner.account,
                                                         author=self.second_owner)

        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertIn(accountgroup.group, possible_groups)
        self.assertNotIn(other_account_group.group, possible_groups)

        request.user = self.second_owner
        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertNotIn(accountgroup.group, possible_groups)
        self.assertIn(other_account_group.group, possible_groups)