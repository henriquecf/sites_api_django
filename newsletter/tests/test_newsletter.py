# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

import test_routines
import test_fixtures
from resource import routines as resource_routines
from newsletter.models import Newsletter


class NewsletterAPITestCase(APILiveServerTestCase):
    model = Newsletter

    def setUp(self):
        self.url = reverse('newsletter-list')
        self.data = {
            'subject': 'First Newsletter',
            'content': 'This is the very first newsletter'
        }
        self.altered_data = {
            'subject': 'First Newsletter altered',
            'content': 'This is the very first newsletter altered'
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

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

    def test_resource_serializer_hyperlinked_fields(self):
        resource_routines.test_resource_serializer_hyperlinked_fields_routine(self, fields=[])

    def test_resource_serializer_read_only_fields(self):
        resource_routines.test_serializer_read_only_fields_routine(self, fields=[])

    def test_resource_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_resource_user_and_account_coincide_with_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_send_newsletter_just_to_own_subscribers(self):
        response = self.client.post(self.url, self.data)
        send_url = response.data['send_newsletter']
        # TODO this test is not complete