import datetime
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase


class AccountAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        # TODO refactor authorization
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ivan')

    def test_create(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 201, response.data)

    def test_default_expiration_date(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['expiration_date'], datetime.date.today() + datetime.timedelta(30))