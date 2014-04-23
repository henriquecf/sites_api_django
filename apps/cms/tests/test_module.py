# -*- coding: utf-8 -*-

import ast, urllib
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from apps.resource.tests import routines as resource_routines
from apps.publication.tests import routines as publication_routines
import test_routines
import test_fixtures
from apps.news.models import News
from apps.cms.models import Module


class ModuleAPITestCase(APILiveServerTestCase):
    model = Module

    def setUp(self):
        self.url = reverse('module-list')
        self.data = {
            'title': 'First Module',
            'model': ContentType.objects.get_for_model(News).id,
            'object_id': None,
            'model_object': None,
            'filters': '{"categories": ["category 1"]}'
        }
        self.altered_data = {
            'title': 'First Module Altered',
            'model': ContentType.objects.get_for_model(News).id,
            'object_id': 1,
            'model_object': 1,
            'filters': '{"categories": ["category 2"]}'
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        news_permisions = Permission.objects.filter(codename__endswith='news')
        for permission in news_permisions:
            self.owner.user_permissions.add(permission)
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

    def test_slug_is_slugified_title(self):
        publication_routines.test_slug_is_slugified_title_routine(self)

    def test_slug_is_unique(self):
        publication_routines.test_slug_is_unique_routine(self)

    def test_has_author(self):
        publication_routines.test_has_author_routine(self)

    def test_is_published_default_true(self):
        publication_routines.test_is_published_default_true_routine(self)

    def test_publish(self):
        publication_routines.test_publish_routine(self)

    def test_unpublish(self):
        publication_routines.test_unpublish_routine(self)

    def test_search_fields(self):
        search_fields = ['title', 'description']
        test_routines.test_search_fields_routine(self, search_fields=search_fields)

    def test_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_publication_serializer_hyperlinked_fields(self):
        publication_routines.test_publication_serializer_hyperlinked_fields_routine(self, [])

    def test_user_and_account_from_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_publication_serializer_read_only_fields(self):
        resource_routines.test_serializer_read_only_fields_routine(self, [])

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_content_url(self):
        self.assertIn('content_url', self.first_object_response.data)
        content_url = self.first_object_response.data['content_url']
        self.assertIn('/news/', content_url)
        content_url_response = self.client.get(content_url)
        self.assertEqual(status.HTTP_200_OK, content_url_response.status_code)
        self.assertDictContainsSubset({'count': 0, 'next': None, 'results': []}, content_url_response.data)
        filter_dict = ast.literal_eval(self.first_object_response.data['filters'])
        get_query = urllib.urlencode(filter_dict)
        self.assertIn(get_query.decode(), content_url)