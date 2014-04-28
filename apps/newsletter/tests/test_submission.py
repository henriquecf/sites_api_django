# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as AuthUser
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase

import test_fixtures
from apps.resource.models import User
from apps.newsletter.models import Submission, Newsletter, Subscription


class SubmissionTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = AuthUser.objects.create_user(username='user', email='user@user.com', password='123')
        User.objects.create(user=self.user, author=self.user, owner=self.user)
        self.subscription = Subscription.objects.create(name='ivan', email='ivan@ivan.com', owner=self.user,
                                                        author=self.user)
        self.subscription = Subscription.objects.create(name='ivan', email='ivan@ivan.com', owner=self.user,
                                                        author=self.user)
        self.newsletter = Newsletter.objects.create(subject='subject', content='content', owner=self.user,
                                                    author=self.user)
        self.submission = Submission.objects.create(newsletter=self.newsletter, subscription=self.subscription,
                                                    owner=self.user, author=self.user)

    def test_submission_send_method(self):
        self.submission.send_newsletter()
        self.assertEqual('sent', self.submission.status)


class SubmissionAPITestCase(APILiveServerTestCase):
    model = Submission

    def setUp(self):
        self.url = reverse('submission-list')
        self.data = {
        }
        self.altered_data = {
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))
