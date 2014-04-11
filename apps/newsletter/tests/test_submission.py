# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

import test_fixtures
from apps.newsletter.models import Submission


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
