import datetime
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from resource.tests import OwnerAndChildrenGenericTest


class AccountAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
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

    def test_default_expiration_date(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.data['expiration_date'], datetime.date.today() + datetime.timedelta(30))