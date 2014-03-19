from copy import copy
from datetime import datetime
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from publication.tests import PublicationGenericTest


class NewsAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('news-list')
        self.data = {
            'title': 'First news',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
            'content': 'My first news',
        }
        self.altered_data = {
            'title': 'First news altered',
            'description': 'First description altered',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
            'content': 'My first news altered',
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
        search_fields = ('title', 'description', 'content')
        self.publication_generic_test.search_fields(search_fields)

    def test_filter_author(self):
        self.publication_generic_test.filter_author()

    def test_if_adds_category(self):
        data2 = copy(self.data)
        category_data = {
            'name': 'Category 1',
            'model_name': 'news',
        }
        category_url = reverse('category-list')
        response = self.client.post(category_url, category_data)
        cat1_url = response.data['url']
        data2.update({'categories': [cat1_url]})
        response2 = self.client.post(self.url, data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['categories'], [cat1_url])