# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.contrib.auth.models import Permission, User as AuthUser
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from apps.resource.tests import routines as resource_routines
from apps.resource.models import User
import test_routines
import test_fixtures
from apps.newsletter.models import Subscription
from apps.newsletter.serializers import SubscriptionSerializer
from apps.newsletter.views import SubscriptionViewSet


class SubscriptionTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(user=self.user, author=self.user, owner=self.user)
        self.subscription = Subscription.objects.create(name='ivan', email='ivan@ivan.com', owner=self.user,
                                                        author=self.user)

    def test_token_is_not_null(self):
        self.assertIsNotNone(self.subscription.token)

    def test_subscription_serializer(self):
        request = HttpRequest()
        request.user = self.user
        subscription_serializer = SubscriptionSerializer(context={'request': request})
        self.assertIn('token', subscription_serializer.Meta.exclude)


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
        newsletter_permisions = Permission.objects.filter(codename__endswith='newsletter')
        submission_permissions = Permission.objects.filter(codename__endswith='submission')
        for permission in newsletter_permisions:
            self.owner.user_permissions.add(permission)
        for permission in submission_permissions:
            self.owner.user_permissions.add(permission)
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
        fields = ['is_active']
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

    def test_deactivate(self):
        self.assertEqual(status.HTTP_201_CREATED, self.first_object_response.status_code)
        response = self.client.post(self.url, self.altered_data)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertTrue(subscription.is_active)
        unsubscribe_response = self.client.post(response.data['unsubscribe'], data={'token': '928374869287348972'})
        self.assertEqual(unsubscribe_response.status_code, status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertTrue(subscription.is_active)
        unsubscribe_response = self.client.post(response.data['unsubscribe'], data={'token': subscription.token})
        self.assertEqual(unsubscribe_response.status_code, status.HTTP_200_OK)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertFalse(subscription.is_active)
        response = self.client.post(self.url, self.altered_data)
        subscription = Subscription.objects.get(email='ivan_morais@yahoo.com.br')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(subscription.is_active)
        unsubscribe_response = self.client.post(response.data['unsubscribe'], data={'token': None})
        self.assertEqual(unsubscribe_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_subscribe_with_same_email_in_different_account(self):
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(2, response.data['count'])
        self.set_authorization_bearer(self.second_owner_token)
        response = self.client.get(self.url)
        self.assertEqual(0, response.data['count'])
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(1, response.data['count'])

    def test_submission_field(self):
        response1 = self.client.post(reverse('newsletter-list'),
                                     data={'subject': 'email subject', 'content': 'Email content'})
        response2 = self.client.get(response1.data['url'])
        response3 = self.client.post(response2.data['send_newsletter'])
        response4 = self.client.get(self.first_object_response.data['url'])
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        self.assertEqual([], response2.data['submissions'], response2.data)
        self.assertEqual(['sent - idan@gmail.com'], response4.data['submissions'])

    def test_token_is_not_returned(self):
        self.assertNotIn('token', self.first_object_response.data)

    def test_view_set_create_method(self):
        response = self.client.get(self.first_object_response.data['url'])
        self.assertTrue(response.data['is_active'])
        subscription = Subscription.objects.get(id=self.first_object_response.data['url'].split('/')[-2])
        self.client.post(self.first_object_response.data['unsubscribe'], {'token': subscription.token})
        response = self.client.get(self.first_object_response.data['url'])
        self.assertFalse(response.data['is_active'])
        response = self.client.post(self.url, {'name': 'Idan', 'email': 'idan@gmail.com'})
        self.assertEqual(response.data['url'], self.first_object_response.data['url'])
        response = self.client.get(self.first_object_response.data['url'])
        self.assertTrue(response.data['is_active'])
