# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
import test_routines
import test_fixtures
from resource import routines as resource_routines
from newsletter.models import Newsletter
from ..models import Subscription, Submission


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
        subscription_permisions = Permission.objects.filter(codename__endswith='subscription')
        submission_permissions = Permission.objects.filter(codename__endswith='submission')
        for permission in subscription_permisions:
            self.owner.user_permissions.add(permission)
        for permission in submission_permissions:
            self.owner.user_permissions.add(permission)
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

    def test_send_when_newsletter_has_two_successful_submissions(self):
        response1 = self.client.post(reverse('subscription-list'),
                                    data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        response2 = self.client.post(reverse('subscription-list'),
                                    data={'name': 'idan', 'email': 'idan@idan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response2.status_code)
        response3 = self.client.post(self.first_object_response.data['send_newsletter'])
        self.assertEqual(status.HTTP_202_ACCEPTED, response3.status_code)
        data = {
            'new': 2,
            'successful': 2,
            'resubmissions': 0,
        }
        self.assertEqual(data, response3.data['submissions'])
        response4 = self.client.post(self.first_object_response.data['send_newsletter'])
        data = {
            'new': 0,
            'successful': 2,
            'resubmissions': 0,
        }
        self.assertEqual(data, response4.data['submissions'])
        self.assertEqual(status.HTTP_202_ACCEPTED, response3.status_code)

    def test_send_when_newsletter_has_three_new_submissions(self):
        response1 = self.client.post(reverse('subscription-list'),
                                    data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        response2 = self.client.post(reverse('subscription-list'),
                                    data={'name': 'idan', 'email': 'idan@idan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response2.status_code)
        response3 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'iran', 'email': 'iran@iran.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response3.status_code)
        response4 = self.client.post(self.first_object_response.data['send_newsletter'])
        self.assertEqual(status.HTTP_202_ACCEPTED, response4.status_code)
        data = {
            'new': 3,
            'successful': 3,
            'resubmissions': 0,
        }
        self.assertEqual(status.HTTP_202_ACCEPTED, response4.status_code)
        self.assertEqual(data, response4.data['submissions'])