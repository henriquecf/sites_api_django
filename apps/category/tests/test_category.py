# -*- coding: utf-8 -*-
from copy import copy
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from rest_framework.test import APILiveServerTestCase

from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.resource.tests import routines as resource_routines
import test_routines
import test_fixtures


class CategoryAPITestCase(APILiveServerTestCase):
    model = Category

    def setUp(self):
        self.url = reverse('category-list')
        self.data = {
            'name': 'Category 1',
            'model': 'uncategorized'
        }
        self.altered_data = {
            'name': 'Category 1 altered',
            'model': 'uncategorized'
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

    def test_resource_hyperlinked_fields(self):
        fields = ['get_descendants']
        resource_routines.test_resource_serializer_hyperlinked_fields_routine(self, fields)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_if_creates_with_parent(self):
        response = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        response2 = self.client.post(self.url, children_data)
        self.assertEqual(response2.data['parent'], response.data['url'])

    def test_get_descendants(self):
        response = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        response2 = self.client.post(self.url, children_data)
        response3 = self.client.get(response.data['url'])
        self.assertIn('get_descendants', response3.data)
        get_descendants_url = response3.data['get_descendants']
        response4 = self.client.get(get_descendants_url)
        self.assertEqual(response4.data['descendants'][0], response2.data)

    def test_is_leaf_node(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('is_leaf_node', response.data)
        self.assertTrue(response.data['is_leaf_node'])
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        self.client.post(self.url, children_data)
        response2 = self.client.get(response.data['url'])
        self.assertFalse(response2.data['is_leaf_node'])

    def test_filter_model_name(self):
        data = copy(self.data)
        data.update({'model': 'other category'})
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code, response.data)
        model_filter = {'model': 'other category'}
        response2 = self.client.get(self.url, model_filter)
        self.assertEqual(1, response2.data['count'], response2.data)

    def test_parent_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertIn(('Category 1', ), possible_parents.values_list('name'))

        other_user_category = Category.objects.create(author=self.second_owner, account=self.second_owner.account,
                                                      name='Other category', model='uncategorized')
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertIn(('Category 1', ), possible_parents.values_list('name'))
        self.assertNotIn(other_user_category, possible_parents)

        request.user = self.second_owner
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertNotIn(('Category 1', ), possible_parents.values_list('name'))
        self.assertIn(other_user_category, possible_parents)