import datetime
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.settings import BASE_DIR, os
from resource.tests import APIGenericTest


class AccountAPITestCase(APILiveServerTestCase):
    fixtures = [os.path.join(BASE_DIR, 'accounts/test_data.json')]

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        self.api_generic_test = APIGenericTest(self)

    def test_create(self):
        self.api_generic_test.create(status_code=status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.api_generic_test.update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        self.api_generic_test.partial_update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        self.api_generic_test.retrieve()

    def test_list(self):
        self.api_generic_test.list()

    def test_destroy(self):
        self.api_generic_test.destroy()

    def test_admin_permission(self):
        self.api_generic_test.admin_permission()

    def test_hyperlinked_field(self):
        accountuser_url = reverse('accountuser-list')
        response = self.client.post(accountuser_url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.api_generic_test.hyperlinked_field('owner')

    def test_default_expiration_date(self):
        self.assertEqual(self.api_generic_test.first_object_response.data['expiration_date'],
                         datetime.date.today() + datetime.timedelta(30))