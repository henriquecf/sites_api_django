# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
import test_routines, test_fixtures
from resource import routines as resource_routines
from newsletter.models import Subscription


class SubscriptionAPITestCase(APILiveServerTestCase):
    model = Subscription

    def setUp(self):
        self.url = reverse('subscription-list')
        self.data = {
            'name': 'Idan',
            'email': 'idan@gmail.com',
        }
        self.altered_data = {
            'name': 'Ivan',
            'email': 'ivan_morais@yahoo.com.br',
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)
        self.data.update({'email': 'ivan@gmail.com'})

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self, count=2)

    def test_serializer_read_only_fields(self):
        fields = ['token', 'active']
        resource_routines.test_serializer_read_only_fields_routine(self, fields)

    def test_hyperlinked_fields(self):
        fields = []
        resource_routines.test_resource_serializer_hyperlinked_fields_routine(self, fields)

    def test_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_user_and_account_coincide_with_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_email_is_unique(self):
        self.client.post(self.url, self.data)
        count = Subscription.objects.count()
        self.client.post(self.url, self.data)
        count_again = Subscription.objects.count()
        self.assertEqual(count, count_again)

    def test_generate_token_string(self):
        subscription = Subscription.objects.get(email='idan@gmail.com')
        self.assertTrue(subscription.token)
        self.assertEqual(str, type(self.first_object_response.data['token']), 'This value must return a str type')

    def test_deactivate(self):
        response = self.client.post(self.url, self.altered_data)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertTrue(subscription.active)
        unsubscribe_response = self.client.get(response.data['unsubscribe'], data={'token': 928374869287348972})
        self.assertEqual(unsubscribe_response.status_code, status.HTTP_401_UNAUTHORIZED)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertTrue(subscription.active)
        unsubscribe_response = self.client.get(response.data['unsubscribe'], data={'token': subscription.token})
        self.assertEqual(unsubscribe_response.status_code, status.HTTP_202_ACCEPTED)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertFalse(subscription.active)
        response = self.client.post(self.url, self.altered_data)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(subscription.active)
