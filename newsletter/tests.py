# -*- coding: utf-8 -*-

from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.tests import PublicationGenericTest
from owner.models import User
from owner.tests import OwnerAndChildrenGenericTest
from .models import Newsletter, Subscription

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

    def test_email_is_unique(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.data['email'], '[Subscription with this Email already exists.]')

    def test_generate_token(self):
        self.owner_generic_test.create()
        subscription = Subscription.objects.get(email='ivan.eng.controle@gmail.com')
        self.assertTrue(subscription.token)


class NewsletterAPITestCase(APILiveServerTestCase):

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
        self.owner_and_children_generic_test = OwnerAndChildrenGenericTest(self)

    def test_create(self):
        self.owner_and_children_generic_test.create()

    def test_list(self):
        self.owner_and_children_generic_test.list()

    def test_retrieve(self):
        self.owner_and_children_generic_test.retrieve()

    def test_update(self):
        self.owner_and_children_generic_test.update()

    def test_partial_update(self):
        self.owner_and_children_generic_test.partial_update()

    def test_destroy(self):
        self.owner_and_children_generic_test.destroy()

    def test_owner_is_request_user(self):
        self.owner_and_children_generic_test.owner_or_children_is_request_user()

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
