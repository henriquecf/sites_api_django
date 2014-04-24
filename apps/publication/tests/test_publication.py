# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from apps.publication.tests import routines as publication_routines
from apps.resource.tests import routines as resource_routines
import test_routines
import test_fixtures
from apps.publication.models import Publication, CustomHTML


class PublicationAPITestCase(APILiveServerTestCase):
    model = Publication

    def setUp(self):
        self.url = reverse('publication-list')
        self.data = {
            'title': 'First publication'
        }
        self.altered_data = {
            'title': 'First publication altered'
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, response.data)
        self.assertEqual(0, response.data['count'])


class CustomHTMLAPITestCase(APILiveServerTestCase):
    model = CustomHTML

    def setUp(self):
        self.url = reverse('customhtml-list')
        self.data = {
            'title': 'First custom HTML',
            'content': 'HTML content',
        }
        self.altered_data = {
            'title': 'First custom HTML altered',
            'content': 'HTML content',
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