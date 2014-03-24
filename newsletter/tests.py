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


class SubmissionAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('subscription-list')
        self.data = {
            'subscription': '',
            'newsletter': '',
            'status': 'Not Sent',
        }
        self.altered_data = {
            'subscription': '',
            'newsletter': '',
            'status': 'Sent',
        }
        self.owner_generic_test = OwnerGenericTest(self)

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
        self.owner_generic_test.owner_is_request_user()


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
        self.owner_generic_test = OwnerGenericTest(self)

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

    def test_owner_is_request_user(self):
        self.publication_generic_test.owner_is_request_user()

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

#TODO: This app is composed of subscribers, newsletters and submissions. All them need to implement Owner behaviour.
#TODO: The newsletter must define a subject and a content.
#TODO: The subscription must define a name and a email.
#TODO: The submission must define foreign keys for the other two models and status field to show the attempt status to send.
#TODO: The subscriptions generates a token needed for subscriber to unsubscribe.
#TODO: When a subscriber unsubscribe, your subscrition is deactivated. It is deleted only when the owner decides to remove it removing related sumbissions too.
#TODO: If someone attempt to subscribe with an existing email, a simple 200 status code is returned and if the subscription was deactivated it will be reactivated.
#TODO: There must be an action in submission to send newsletter to the corresponding subscription.
#TODO: When the submission is created it should attempt to send the newsletter and hold the status. If it fail, it must be possible to try again later.
#TODO: A submission that has been sent succefully do not must be sent again in no way.
#TODO: The newsletter must implement an action to send it that creates submissions for all subscriptions and call the submissions send action.
#TODO: If a newsletter is sent again, it will create submissions for all those subscriptions that do not have yet and attempt to send all submissions that failed or have not been sent.
