# -*- coding: utf-8 -*-
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.test import LiveServerTestCase
from django.http import HttpRequest
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from apps.resource.models import Group, AuthUser, User
from apps.resource.serializers import AuthGroupSerializer
from apps.resource.views import GroupViewSet
from apps.resource.exceptions import BadRequestValidationError
from test_fixtures import user_accountuser_account_permissions_token_fixture
import test_routines


class GroupTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(user=user, author=user, owner=user)
        self.group = Group.objects.create(owner=user, author=user, role='My group')
        self.user = user

    def test_model_save_method(self):
        group_name = 'user - My group'
        self.assertEqual(group_name, self.group.group.name)
        self.group.role = 'Ohh'
        self.group.save()
        group_name = 'user - Ohh'
        self.assertEqual(group_name, self.group.group.name)

    def test_authgroup_serializer(self):
        authgroup_serializer = AuthGroupSerializer
        fields = ('id', 'permissions')

        for field in fields:
            self.assertIn(field, authgroup_serializer.Meta.fields)

    def test_pre_save_method(self):
        group = Group(role='test role')
        request = HttpRequest()
        request.user = self.user

        viewset = GroupViewSet(request=request)

        viewset.pre_save(group)

        self.assertEqual(self.user, group.owner)
        self.assertEqual(self.user, group.author)

        group.save()

        try:
            viewset.pre_save(group)
            self.assertFalse('It must not be possible to save to groups with the same role name')
        except BadRequestValidationError:
            pass


class GroupAPITestCase(APILiveServerTestCase):
    model = Group

    def setUp(self):
        self.url = reverse('group-list')
        self.data = {
            'role': 'Group'
        }
        self.altered_data = {
            'role': 'Group altered'
        }
        user_accountuser_account_permissions_token_fixture(self)
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
        self.assertEqual(1, response.data['count'], response.data)

    def test_destroy(self):
        response = self.client.delete(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_search_fields(self):
        fields = ['role']
        test_routines.test_search_fields_routine(self, search_fields=fields)

    def test_hyperlinked_fields(self):
        fields = []
        test_routines.test_serializer_hyperlinked_fields_routine(self, fields=fields)

    def test_read_only_fields(self):
        fields = []
        test_routines.test_serializer_read_only_fields_routine(self, fields=fields)

    def test_role_and_account_are_unique_together(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Should not be possible to create another account group with same role name')
        self.set_authorization_bearer(self.second_owner_token)
        response2 = self.client.post(self.url, self.data)
        self.assertEqual(status.HTTP_201_CREATED, response2.status_code, response2.data)

    def test_assign_unassign_permissions_action(self):
        try:
            assign_perms_url = self.first_object_response.data['assign_permissions']
        except KeyError:
            self.assertFalse('No assign_permissions action found in group')
        permission_queryset = Permission.objects.filter(codename__endswith='group')
        permission_list = []
        for permission in permission_queryset:
            permission_list.append(permission.id)

        response = self.client.post(assign_perms_url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        response = self.client.post(assign_perms_url, data={'perms': permission_list})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

        response = self.client.post(assign_perms_url, data={'permissions': permission_list})
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(permission_list, response.data['assigned_permissions'], response.data)

        group_id = self.first_object_response.data['url'].split('/')[-2]
        group = Group.objects.get(id=group_id)
        self.assertEqual(list(permission_queryset), list(group.group.permissions.all()))

        try:
            unassign_perms_url = self.first_object_response.data['unassign_permissions']
        except KeyError:
            self.assertFalse('No unassign_permissions action found in group')

        response = self.client.post(unassign_perms_url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        response = self.client.post(unassign_perms_url, data={'perms': permission_list})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

        response = self.client.post(unassign_perms_url, data={'permissions': permission_list})
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual([], list(group.group.permissions.all()))

        permission_list.append(1273817)
        response = self.client.post(assign_perms_url, data={'permissions': permission_list})
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertEqual(list(permission_queryset), list(group.group.permissions.all()))