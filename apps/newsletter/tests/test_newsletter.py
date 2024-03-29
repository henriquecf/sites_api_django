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
from apps.newsletter.models import Newsletter, Subscription


class NewsletterTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = AuthUser.objects.create_user(username='user', password='123')
        self.user2 = AuthUser.objects.create_user(username='user2', password='123')
        User.objects.create(user=self.user, author=self.user, owner=self.user)
        User.objects.create(user=self.user2, author=self.user2, owner=self.user2)
        self.subscription = Subscription.objects.create(name='ivan', email='ivan@ivan.com', owner=self.user,
                                                        author=self.user)
        self.subscription2 = Subscription.objects.create(name='idan', email='idan@idan.com', owner=self.user,
                                                         author=self.user)
        self.newsletter = Newsletter.objects.create(subject='subject', content='content', owner=self.user,
                                                    author=self.user)
        self.request = HttpRequest()

    def test_send_newsletter_method(self):
        status = self.newsletter.send_newsletter(self.user)
        expected = dict(new=2,
                        successful=2,
                        failed=0,
                        resubmissions=0)
        self.assertEqual(expected, status)
        status = self.newsletter.send_newsletter(self.user)
        expected = dict(new=0,
                        successful=2,
                        failed=0,
                        resubmissions=0)
        self.assertEqual(expected, status)

    def test_send_newsletter_method_with_different_owner(self):
        status = self.newsletter.send_newsletter(self.user2)
        expected = dict(new=0,
                        successful=0,
                        failed=0,
                        resubmissions=0)
        self.assertEqual(expected, status)


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

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_send_newsletter_just_to_own_subscribers(self):
        self.set_authorization_bearer(self.second_owner_token)
        response = self.client.post(self.url, self.data)
        response1 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        self.set_authorization_bearer(self.owner_token)
        response1 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        response = self.client.post(self.url, self.data)
        send_url = response.data['send_newsletter']
        response2 = self.client.post(send_url)
        data = {
            'new': 1,
            'successful': 1,
            'resubmissions': 0,
            'failed': 0,
        }
        self.assertEqual(data, response2.data['submissions'], response2.data)
        self.assertEqual(status.HTTP_200_OK, response2.status_code)

    def test_send_when_newsletter_has_two_successful_submissions(self):
        response1 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        response2 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'idan', 'email': 'idan@idan.com.br'})
        self.assertEqual(status.HTTP_201_CREATED, response2.status_code)
        response3 = self.client.post(self.first_object_response.data['send_newsletter'])
        self.assertEqual(status.HTTP_200_OK, response3.status_code)
        data = {
            'new': 2,
            'successful': 2,
            'resubmissions': 0,
            'failed': 0,
        }
        self.assertEqual(data, response3.data['submissions'])
        response4 = self.client.post(self.first_object_response.data['send_newsletter'])
        data = {
            'new': 0,
            'successful': 2,
            'resubmissions': 0,
            'failed': 0,
        }
        self.assertEqual(data, response4.data['submissions'])
        self.assertEqual(status.HTTP_200_OK, response3.status_code)

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
        self.assertEqual(status.HTTP_200_OK, response4.status_code)
        data = dict(new=3, successful=3, resubmissions=0, failed=0)
        self.assertEqual(status.HTTP_200_OK, response4.status_code)
        self.assertEqual(data, response4.data['submissions'])

    def test_submission_field(self):
        response1 = self.client.post(reverse('subscription-list'),
                                     data={'name': 'ivan', 'email': 'ivan@ivan.com.br'})
        response2 = self.client.get(self.url)
        response3 = self.client.post(self.first_object_response.data['send_newsletter'])
        response4 = self.client.get(self.url)
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        self.assertEqual([], response2.data['results'][0]['submissions'], response2.data)
        self.assertEqual(['sent - ivan@ivan.com.br'], response4.data['results'][0]['submissions'])