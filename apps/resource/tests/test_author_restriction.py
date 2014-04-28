# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.http.request import HttpRequest
from django.test import LiveServerTestCase
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from apps.resource.models import Group, User, AuthorRestriction, AuthUser, AuthGroup
from apps.resource.serializers import AuthorRestrictionSerializer

from test_fixtures import user_accountuser_account_permissions_token_fixture
import test_routines


class AuthorRestrictionTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(user=user, owner=user, author=user)
        perm = Permission.objects.first()
        author_restriction = AuthorRestriction.objects.create(owner=user, author=user, user=user, permission=perm,
                                                              filter_values=user.id)
        self.author_restriction = author_restriction
        self.perm = perm
        self.user = user

    def test_model_save_delete_methods(self):
        self.assertIn(self.perm, self.user.user_permissions.all())
        self.author_restriction.delete()
        self.assertNotIn(self.perm, self.user.user_permissions.all())

        group = Group.objects.create(owner=self.user, author=self.user, role='group')
        self.user.groups.add(group.group)

        author_rest = AuthorRestriction.objects.create(owner=self.user, author=self.user, group=group.group,
                                                       filter_values=self.user.id, permission=self.perm)
        self.assertIn(self.perm, group.group.permissions.all())
        author_rest.delete()
        self.assertNotIn(self.perm, group.group.permissions.all())

    def test_serializer_get_fields_method(self):
        request = HttpRequest()

        other_user = AuthUser.objects.create_user(username='other_user', password='123')
        User.objects.create(user=other_user, owner=other_user, author=other_user)
        other_user_group = Group.objects.create(owner=other_user, author=other_user, role='other group')

        AuthorRestriction.objects.create(owner=other_user, author=other_user, user=other_user, permission=self.perm,
                                         filter_values=other_user.id)
        AuthorRestriction.objects.create(owner=other_user, author=other_user, group=other_user_group.group,
                                         permission=self.perm, filter_values=other_user.id)

        group = Group.objects.create(owner=self.user, author=self.user, role='group')
        AuthorRestriction.objects.create(owner=self.user, author=self.user, group=group.group, permission=self.perm,
                                         filter_values=self.user.id)

        request.user = self.user
        serializer = AuthorRestrictionSerializer(context={'request': request})

        queryset = serializer.get_fields()['user'].queryset
        self.assertEqual(1, queryset.count())
        self.assertEqual(list(AuthUser.objects.filter(user__owner=self.user.user.owner)), list(queryset))

        queryset = serializer.get_fields()['group'].queryset
        self.assertEqual(1, queryset.count())
        self.assertEqual(list(AuthGroup.objects.filter(group__owner=self.user.user.owner)), list(queryset))

        request.user = other_user

        queryset = serializer.get_fields()['user'].queryset
        self.assertEqual(1, queryset.count())
        self.assertEqual(list(AuthUser.objects.filter(user__owner=other_user.user.owner)), list(queryset))

        queryset = serializer.get_fields()['group'].queryset
        self.assertEqual(1, queryset.count())
        self.assertEqual(list(AuthGroup.objects.filter(group__owner=other_user.user.owner)), list(queryset))


class AuthorRestrictionAPITestCase(APILiveServerTestCase):
    model = AuthorRestriction

    def setUp(self):
        self.url = reverse('authorrestriction-list')
        user_accountuser_account_permissions_token_fixture(self)
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

    def alter_data(self, user_id=None, altered_data=False):
        if not altered_data:
            data = self.data
        else:
            data = self.altered_data
        if not user_id:
            user_id = self.second_owner.id
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

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self, alter_data=True)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

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
        accountgroup = Group.objects.create(role='Test role', owner=self.owner,
                                                  author=self.owner)
        self.data.update({'group': accountgroup.group.id})
        test_routines.test_api_basic_methods_routine(self)

    def test_permission_is_assigned_and_unassigned_to_group(self):
        self.data.pop('user')
        accountgroup = Group.objects.create(role='Test role', owner=self.owner,
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

        other_account_user = AuthUser.objects.create_user(username='other_user', password='123')
        User.objects.create(user=other_account_user, owner=self.second_owner, author=self.second_owner)

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
        accountgroup = Group.objects.create(role='group', owner=self.owner, author=self.owner)

        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertIn(accountgroup.group, possible_groups)

        other_account_group = Group.objects.create(role='other_group', owner=self.second_owner,
                                                         author=self.second_owner)

        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertIn(accountgroup.group, possible_groups)
        self.assertNotIn(other_account_group.group, possible_groups)

        request.user = self.second_owner
        possible_groups = AuthorRestrictionSerializer(context={'request': request}).get_fields()['group'].queryset
        self.assertNotIn(accountgroup.group, possible_groups)
        self.assertIn(other_account_group.group, possible_groups)