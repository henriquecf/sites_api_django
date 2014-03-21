from copy import copy
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from owner.tests import OwnerGenericTest


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

    def add_category(self, model_name):
        data2 = copy(self.data)
        category_data = {
            'name': 'Category 1',
            'model_name': model_name,
        }
        category_url = reverse('category-list')
        response = self.test_case.client.post(category_url, category_data)
        cat1_url = response.data['url']
        data2.update({'categories': [cat1_url]})
        response2 = self.test_case.client.post(self.url, data2)
        self.test_case.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        try:
            model_categories = response2.data['categories']
        except KeyError:
            model_categories = None
        self.test_case.assertEqual(model_categories, [cat1_url],
                                   'Field categories not found in model "{0}"'.format(model_name))


class PublicationAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('publication-list')
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


class CategoryAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('category-list')
        self.data = {
            'name': 'Category 1',
            'model_name': 'news',
        }
        self.altered_data = {
            'name': 'Category 1 Altered',
            'model_name': 'news',
        }
        self.owner_generic_test = OwnerGenericTest(self)

    def test_create(self):
        self.owner_generic_test.create()

    def test_retrieve(self):
        self.owner_generic_test.retrieve()

    def test_list(self):
        self.owner_generic_test.list()

    def test_update(self):
        self.owner_generic_test.update()

    def test_partial_update(self):
        self.owner_generic_test.partial_update()

    def test_destroy(self):
        self.owner_generic_test.destroy()

    def test_owner_is_request_user(self):
        self.owner_generic_test.owner_is_request_user()

    def test_if_creates_with_parent(self):
        response = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        response2 = self.client.post(self.url, children_data)
        self.assertEqual(response2.data['parent'], response.data['url'])

    def test_get_descendants(self):
        response = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        response2 = self.client.post(self.url, children_data)
        response3 = self.client.get(response.data['url'])
        self.assertIn('get_descendants', response3.data)
        get_descendants_url = response3.data['get_descendants']
        response4 = self.client.get(get_descendants_url)
        self.assertEqual(response4.data['descendants'][0], response2.data)

    def test_is_leaf_node(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('is_leaf_node', response.data)
        self.assertTrue(response.data['is_leaf_node'])
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        self.client.post(self.url, children_data)
        response2 = self.client.get(response.data['url'])
        self.assertFalse(response2.data['is_leaf_node'])