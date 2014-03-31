from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from publication.tests import PublicationGenericTest


class FileAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('file-list')
        self.data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
        }
        self.altered_data = {
            'title': 'First publication altered',
            'description': 'First description altered',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
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

    def test_add_category(self):
        self.publication_generic_test.add_category('file')

    def test_owner_is_request_user(self):
        self.publication_generic_test.owner_is_request_user()

    def test_hyperlinked_fields(self):
        self.publication_generic_test.hyperlinked_fields([])

    def test_user_and_account_from_request_user(self):
        self.publication_generic_test.user_and_account_from_request_user()