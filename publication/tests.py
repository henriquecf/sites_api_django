from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from accounts.tests import OwnerGenericTest


class PublicationGenericTest(OwnerGenericTest):
    def slug_is_slugified_title(self, slug_repeat_number='-2'):
        response = self.test_case.client.post(self.url, self.data)
        self.test_case.assertEqual(response.data['slug'], slugify(response.data['title']) + slug_repeat_number,
                                   'Slug is not slugified title')

    def slug_is_unique(self):
        self.slug_is_slugified_title(slug_repeat_number='-2')
        self.slug_is_slugified_title(slug_repeat_number='-3')
        self.slug_is_slugified_title(slug_repeat_number='-4')

    def has_author(self):
        self.test_case.assertIn('author', self.first_object_response.data, 'Response has no field "author"')
        self.test_case.assertEqual(self.first_object_response.data['author'], self.username_or_token,
                                   'Unexpected author name returned')

    def is_published_default_true(self):
        self.test_case.assertIn('is_published', self.first_object_response.data, 'Response has no field "is_published"')
        self.test_case.assertTrue(self.first_object_response.data['is_published'],
                                  'Is_published default value must be True')

    def get_action_response(self, action_name, status_code=status.HTTP_200_OK):
        action_url = self.first_object_response.data[action_name]
        print(action_url)
        response = self.test_case.client.get(action_url)
        self.test_case.assertEqual(response.status_code, status_code)
        return response

    def unpublish(self):
        response = self.get_action_response('unpublish')
        self.test_case.assertFalse(response.data['is_published'], 'Is_published return must be False')

    def publish(self):
        response = self.get_action_response('publish')
        self.test_case.assertTrue(response.data['is_published'], 'Is_published return must be True')

    def filter_author(self):
        filter_data = {'author': self.username_or_token}
        response = self.test_case.client.get(self.url, filter_data)
        self.test_case.assertEqual(response.data['count'], 1)
        filter_data.update({'author': 'another_author'})
        response2 = self.test_case.client.get(self.url, filter_data)
        self.test_case.assertEqual(response2.data['count'], 0, 'Filter not working')


class PublicationAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('publication-list')
        self.data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        self.altered_data = {
            'title': 'First publication altered',
            'description': 'First description altered',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
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