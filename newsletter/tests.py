# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from resource.tests import ResourceGenericTest
from .models import Subscription, Newsletter


#TODO: Test just resource can destroy or user with unsubscription code can destroy
class SubscriptionAPITestCase(APILiveServerTestCase):
    model = Subscription

    def setUp(self):
        self.url = reverse('subscription-list')
        self.data = {
            'name': 'Idan',
            'email': 'ivan.eng.controle@gmail.com',
        }
        self.altered_data = {
            'name': 'Ivan',
            'email': 'ivan_morais@yahoo.com.br',
        }
        self.resource_generic_test = ResourceGenericTest(self)

    def test_create(self):
        self.resource_generic_test.create()

    def test_list(self):
        self.data.update({'email': 'ivan2@ivan2.com'})
        self.resource_generic_test.list(count=1)

    def test_retrieve(self):
        self.resource_generic_test.retrieve()

    def test_update(self):
        self.resource_generic_test.update()

    def test_partial_update(self):
        self.resource_generic_test.partial_update()

    def test_destroy(self):
        self.resource_generic_test.destroy()

    def test_email_is_unique(self):
        count = Subscription.objects.count()
        self.client.post(self.url, self.data)
        count_again = Subscription.objects.count()
        self.assertEqual(count, count_again)

    def test_generate_token(self):
        subscription = Subscription.objects.get(email='ivan.eng.controle@gmail.com')
        self.assertTrue(subscription.token)

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(subscription.active)

    def test_model_has_custom_permission(self):
        self.resource_generic_test.model_has_custom_permission()

    def test_serializer_read_only_fields(self):
        self.resource_generic_test.serializer_read_only_fields([])


class NewsletterAPITestCase(APILiveServerTestCase):
    model = Newsletter

    def setUp(self):
        self.url = reverse('newsletter-list')
        self.data = {
            'subject': 'First newsletter',
            'content': 'My content',
        }
        self.altered_data = {
            'subject': 'First newsletter altered',
            'content': 'My content altered',
        }
        self.resource_generic_test = ResourceGenericTest(self)

    def test_create(self):
        self.resource_generic_test.create()

    def test_list(self):
        self.resource_generic_test.list()

    def test_retrieve(self):
        self.resource_generic_test.retrieve()

    def test_update(self):
        self.resource_generic_test.update()

    def test_partial_update(self):
        self.resource_generic_test.partial_update()

    def test_destroy(self):
        self.resource_generic_test.destroy()

    def test_send_newsletter_just_to_own_subscribers(self):
        response = self.client.post(self.url, self.data)
        send_url = response.data['send_newsletter']
        # TODO this test is not complete

    def test_model_has_custom_permission(self):
        self.resource_generic_test.model_has_custom_permission()

    def test_serializer_read_only_fields(self):
        self.resource_generic_test.serializer_read_only_fields([])
