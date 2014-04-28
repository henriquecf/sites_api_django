# -*- coding: utf-8 -*-
from copy import copy
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User as AuthUser
from django.http.request import HttpRequest
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from apps.resource.models import Resource, User
from apps.publication.models import Publication
from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.category.views import CategoryViewSet
from apps.resource.tests import routines as resource_routines
import test_routines
import test_fixtures


class CategoryTestCase(LiveServerTestCase):
    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        self.model = ContentType.objects.get_for_model(Category)
        self.category = Category.objects.create(author=user, owner=user, name='Test', model=self.model)
        self.user = user
        self.request = HttpRequest()
        self.request.user = user

    def test_get_descendants_method(self):
        self.request.META['SERVER_NAME'] = 'testserver'
        self.request.META['SERVER_PORT'] = 8080
        child_category = Category.objects.create(author=self.user, owner=self.user, name='Child Test', model=self.model,
                                                 parent=self.category)
        viewset = CategoryViewSet(context={'request': self.request}, request=self.request, filter_backends=None)
        viewset.kwargs = {'lookup_url_field': self.category.id, 'pk': self.category.id}
        descendants = viewset.get_descendants(self.request).data['descendants']
        self.assertEqual(1, len(descendants))
        self.assertEqual(child_category.name, descendants[0]['name'])
        child_id = int(descendants[0]['url'].split('/')[-2])
        self.assertEqual(child_category.id, child_id)

        child_category.parent = None
        child_category.save()

        descendants = viewset.get_descendants(self.request).data['descendants']
        self.assertEqual(0, len(descendants))

    def test_get_fields_method(self):
        serializer = CategorySerializer(context={'request': self.request})
        queryset = serializer.get_fields()['parent'].queryset
        self.assertEqual(1, queryset.count())
        self.assertEqual(self.category, queryset[0])
        other_user = AuthUser.objects.create_user(username='user2', password='123')
        User.objects.create(owner=other_user, author=other_user, user=other_user)
        Category.objects.create(owner=other_user, author=other_user, name='Other cat', model=self.model)
        self.assertEqual(1, queryset.count())
        self.assertEqual(self.category, queryset[0])
        cat2 = Category.objects.create(owner=self.user, author=self.user, name='Another Category', model=self.model)
        self.assertEqual(2, queryset.count())
        self.assertEqual(self.category, queryset[0])
        self.assertEqual(cat2, queryset[1])


class CategoryAPITestCase(APILiveServerTestCase):
    model = Category

    def setUp(self):
        self.url = reverse('category-list')
        resource_content_type = ContentType.objects.get_for_model(Resource)
        self.data = {
            'name': 'Category 1',
            'model': resource_content_type.id,
        }
        self.altered_data = {
            'name': 'Category 1 altered',
            'model': resource_content_type.id,
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
        other_category_content_type = ContentType.objects.get_for_model(Publication)
        data.update({'model': other_category_content_type.id})
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code, response.data)
        model_filter = {'model': other_category_content_type.id}
        response2 = self.client.get(self.url, model_filter)
        self.assertEqual(1, response2.data['count'], response2.data)
        self.client.post(self.url, self.data)
        response2 = self.client.get(self.url, model_filter)
        self.assertEqual(1, response2.data['count'], response2.data)
        self.client.post(self.url, data)
        response2 = self.client.get(self.url, model_filter)
        self.assertEqual(2, response2.data['count'], response2.data)

    def test_parent_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertIn(('Category 1', ), possible_parents.values_list('name'))
        resource_content_type = ContentType.objects.get_for_model(Resource)
        other_user_category = Category.objects.create(author=self.second_owner, owner=self.second_owner,
                                                      name='Other category', model=resource_content_type)
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertIn(('Category 1', ), possible_parents.values_list('name'))
        self.assertNotIn(other_user_category, possible_parents)

        request.user = self.second_owner
        possible_parents = CategorySerializer(context={'request': request}).get_fields()['parent'].queryset
        self.assertNotIn(('Category 1', ), possible_parents.values_list('name'))
        self.assertIn(other_user_category, possible_parents)