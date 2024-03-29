# -*- coding: utf-8 -*-

import ast
from django.http import HttpRequest
from django.test import LiveServerTestCase
from apps.cms.serializers import ModuleSerializer
from apps.resource.models import User

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User as AuthUser
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from apps.resource.tests import routines as resource_routines
from apps.publication.tests import routines as publication_routines
import test_routines
import test_fixtures
from apps.news.models import News
from apps.cms.models import Module, Page, ModulePosition


class ModuleSerializerTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        self.user = user
        self.request = HttpRequest()
        self.request.user = user
        self.serializer = ModuleSerializer(context={'request': self.request},
                                           data={'owner': user, 'author': user, 'title': 'Module', 'model': Page})

    def test_serializer_model_field(self):
        models = self.serializer.get_fields()['model'].queryset.all()
        excluded_models = ContentType.objects.filter(app_label__in=(
            'admin', 'auth', 'contenttypes', 'oauth2_provider', 'sessions', 'sites', 'resource', 'cms', 'newsletter',
            'category'))
        self.assertNotIn(excluded_models, models)
        self.assertIn(ContentType.objects.get_for_model(News), models)


class ModuleTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        page = Page.objects.create(owner=user, author=user, title='Page')
        self.user = user
        self.request = HttpRequest()
        self.request.user = user
        self.model = ContentType.objects.get_for_model(Page)
        self.module = Module.objects.create(owner=user, author=user, title='Module', model=self.model)
        ModulePosition.objects.create(title=self.module.title, page=page, module=self.module, position='1', order=1,
                                      owner=user, author=user)
        self.module.save()

    def test_serializer_get_content_url(self):
        self.request.META['SERVER_NAME'] = 'testserver'
        self.request.META['SERVER_PORT'] = 8080
        self.module.filters = '{"test": "OK"}'
        generated_filter = 'test=OK'
        module_serializer = ModuleSerializer(context={'request': self.request})
        content_url = module_serializer.get_content_url(self.module)
        self.assertIn(generated_filter, content_url)
        self.assertIn('?', content_url)
        self.module.filters = '{"test": "OK"'
        content_url = module_serializer.get_content_url(self.module)
        self.assertNotIn(generated_filter, content_url)
        self.assertNotIn('?', content_url)


class ModuleAPITestCase(APILiveServerTestCase):
    model = Module

    def setUp(self):
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        page_permisions = Permission.objects.filter(codename__endswith='page')
        for permission in page_permisions:
            self.owner.user_permissions.add(permission)
        page_response = self.client.post(reverse('page-list'), {'title': 'A pages'})
        self.url = reverse('module-list')
        self.data = {
            'title': 'First Module',
            'model': ContentType.objects.get_for_model(News).id,
            'object_id': None,
            'model_object': None,
            'filters': '{"categories": ["category 1"]}',
            'pages': {'page': page_response.data['url'], 'position': '1', 'order': 1},
        }
        self.altered_data = {
            'title': 'First Module Altered',
            'model': ContentType.objects.get_for_model(News).id,
            'object_id': 1,
            'model_object': 1,
            'filters': '{"categories": ["category 2"]}',
            'pages': {'page': page_response.data['url'], 'position': '1', 'order': 1},
        }
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
        try:
            get_query = urlencode(filter_dict).decode()
        except AttributeError:
            get_query = urlencode(filter_dict)
        self.assertIn(get_query, content_url)
        self.assertIn('?', content_url)
        response = self.client.patch(self.first_object_response.data['url'], {'filters': ''})
        self.assertNotIn('?', response.data['content_url'])
