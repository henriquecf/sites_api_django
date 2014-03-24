# -*- coding: utf-8 -*-

from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.tests import PublicationGenericTest
from owner.tests import OwnerAndChildrenGenericTest

#TODO: Test just owner can destroy or user with unsubscription code can destroy

class SubscpritionAPITestCase(APILiveServerTestCase):

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
        self.owner_generic_test = OwnerAndChildrenGenericTest(self)

    def test_create(self):
        self.owner_generic_test.create()

    def test_list(self):
        self.owner_generic_test.list()

    def test_retrieve(self):
        self.owner_generic_test.retrieve()

    def test_update(self):
        self.owner_generic_test.update()

    def test_partial_update(self):
        self.owner_generic_test.partial_update()

    def test_destroy(self):
        self.owner_generic_test.destroy()

    def test_owner_is_user_request(self):
        self.owner_generic_test.owner_or_children_is_request_user()
'''
    def test_user_destroy(self):
        response = self.client.post(self.url, self.data)
        subscription = Subscriptions.objects.get(email=response.data['email'])
        self.owner_generic_test.set_authorization(random_user=True)
        response2 = self.client.get(response.data['unsubscribe'], {'code': subscription.code})
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.owner_generic_test.reset_authorization()
        response2 = self.client.get(response.data['unsubscribe'], {'code': 'ASPO29348734582j'})
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        response2 = self.client.get(response.data['unsubscribe'], {'code': subscription.code})
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
'''

class NewsletterAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('newsletter-list')
        self.data = {
            'title': 'First newsletter',
            'description': 'First description',
            'slug': 'first-newsletter',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
            'content': 'My content',
        }
        self.altered_data = {
            'title': 'First newsletter altered',
            'description': 'First description altered',
            'slug': 'first-newsletter',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
            'content': 'My content altered',
        }
        self.publication_generic_test = PublicationGenericTest(self)

    def test_create(self):
        self.publication_generic_test.create()

    def test_list(self):
        self.publication_generic_test.list()

    def test_retrieve(self):
        self.publication_generic_test.retrieve()

    def test_update(self):
        self.publication_generic_test.update()

    def test_partial_update(self):
        self.publication_generic_test.partial_update()

    def test_destroy(self):
        self.publication_generic_test.destroy()

    def test_owner_is_request_user(self):
        self.publication_generic_test.owner_or_children_is_request_user()

    def test_slug_is_slugified_title(self):
        self.publication_generic_test.slug_is_slugified_title()

    def test_slug_is_unique(self):
        self.publication_generic_test.slug_is_unique()

    def test_has_author(self):
        self.publication_generic_test.has_author()

    def test_is_published_default_true(self):
        self.publication_generic_test.is_published_default_true()

    def test_publish(self):
        self.publication_generic_test.publish()

    def test_unpublish(self):
        self.publication_generic_test.unpublish()

    def test_search_fields(self):
        search_fields = ('title', 'description')
        self.publication_generic_test.search_fields(search_fields)

    def test_filter_author(self):
        self.publication_generic_test.filter_author()

    def test_send_newsletter(self):
        request = self.client.post(self.url, self.data)
        send_url = request.data['send_newsletter']
        request2 = self.client.get(send_url)
        self.assertEqual(request2.status_code, status.HTTP_200_OK)
        response = self.client.post(self.url, self.data)
        send_url = response.data['send_newsletter']
        response2 = self.client.get(send_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_send_newsletter_just_to_own_subscribers(self):
        response = self.client.post(self.url, self.data)
        send_url = response.data['send_newsletter']

    #TODO: Remove publication dependency of newsletter
    #TODO: Test submissions creation when newsletter is sent
    #TODO: Test submission status equal to fail when fail to send
    #TODO: Test submission status equal to sent when succeeds to send
    #TODO: Test submission resend just send fail submissions
    #TODO: Test submit action submits newsletter to just own subscribers
    #TODO: Test just owner can submit a newsletter
