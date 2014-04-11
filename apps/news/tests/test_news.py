# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from apps.category.tests.routines import test_add_category_routine, test_filter_categories
from apps.publication.tests import routines as publication_routines
from apps.resource import routines as resource_routines
import test_routines
import test_fixtures
from apps.news.models import News


class NewsAPITestCase(APILiveServerTestCase):
    model = News

    def setUp(self):
        self.url = reverse('news-list')
        self.data = {
            'title': 'First news',
            'content': 'Content',
        }
        self.altered_data = {
            'title': 'First news altered',
            'content': 'Content altered',
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

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
        fields = ['title', 'description', 'content']
        test_routines.test_search_fields_routine(self, search_fields=fields)

    def test_resource_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_publication_serializer_hyperlinked_fields(self):
        publication_routines.test_publication_serializer_hyperlinked_fields_routine(self, fields=[])

    def test_resource_user_and_account_coincide_with_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_resource_serializer_read_only_fields(self):
        resource_routines.test_resource_serializer_read_only_fields_routine(self, fields=[])

    def test_add_category(self):
        test_add_category_routine(self)

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

    def test_filter_categories(self):
        test_filter_categories(self)

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)