# -*- coding: utf-8 -*-
from copy import copy
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

import routines
import fixtures
from publication import routines as publication_routines
from resource import routines as resource_routines
from publication.models import Publication


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
        fixtures.user_accountuser_account_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_api_basic_methods(self):
        routines.test_api_basic_methods_routine(self)

    def test_resource_permission(self):
        routines.test_resource_permission_routine(self)

    def test_admin_permission(self):
        routines.test_admin_permission_routine(self)

    def test_custom_object_permission(self):
        routines.test_custom_object_permission_routine(self)

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
        routines.test_search_fields_routine(self, search_fields=search_fields)

    def test_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_publication_serializer_hyperlinked_fields(self):
        publication_routines.test_publication_serializer_hyperlinked_fields_routine(self, [])

    def test_user_and_account_from_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_model_has_custom_permission(self):
        routines.test_model_has_custom_permission_routine(self)

    def test_publication_serializer_read_only_fields(self):
        resource_routines.test_serializer_read_only_fields_routine(self, [])