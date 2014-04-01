import datetime
from copy import copy
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.test.testcases import LiveServerTestCase
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from resource.tests import ResourceGenericTest
from account.models import Account
from .models import Publication, Category


class PublicationGenericTest(ResourceGenericTest):

    def slug_is_slugified_title(self, slug_repeat_number='-2'):
        response = self.test_case.client.post(self.url, self.data)
        self.test_case.assertEqual(response.data['slug'], slugify(response.data['title']) + slug_repeat_number,
                                   'Slug is not slugified title')

    def slug_is_unique(self):
        self.slug_is_slugified_title(slug_repeat_number='-2')
        self.slug_is_slugified_title(slug_repeat_number='-3')
        self.slug_is_slugified_title(slug_repeat_number='-4')

    def has_author(self):
        self.test_case.assertIn('creator', self.first_object_response.data, 'Response has no field "creator"')

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

    def hyperlinked_fields(self, fields):
        if not fields:
            fields = ['is_published', 'publish', 'unpublish']
        else:
            fields.append('is_published')
            fields.append('publish')
            fields.append('unpublish')
        super(PublicationGenericTest, self).hyperlinked_fields(fields)

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
    model = Publication

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

    def test_owner_is_request_user(self):
        self.publication_generic_test.owner_is_request_user()

    def test_hyperlinked_fields(self):
        self.publication_generic_test.hyperlinked_fields([])

    def test_user_and_account_from_request_user(self):
        self.publication_generic_test.user_and_account_from_request_user()

    def test_model_has_custom_permission(self):
        self.publication_generic_test.model_has_custom_permission()


class CategoryAPITestCase(APILiveServerTestCase):
    model = Category

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
        self.resource_generic_test = ResourceGenericTest(self)

    def test_create(self):
        self.resource_generic_test.create()

    def test_retrieve(self):
        self.resource_generic_test.retrieve()

    def test_list(self):
        self.resource_generic_test.list()

    def test_update(self):
        self.resource_generic_test.update()

    def test_partial_update(self):
        self.resource_generic_test.partial_update()

    def test_destroy(self):
        self.resource_generic_test.destroy()

    def test_hyperlinked_fields(self):
        fields = ['get_descendants']
        self.resource_generic_test.hyperlinked_fields(fields)

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

    def test_model_has_custom_permission(self):
        self.resource_generic_test.model_has_custom_permission()


class PublicationTestCase(LiveServerTestCase):

    def setUp(self):
        user = User.objects.create_user('henrique', '123')
        account = Account.objects.create(owner=user, expiration_date=datetime.date.today())
        self.publication = Publication.objects.create(title='Test', account=account, creator=user)
        self.yesterday = timezone.now() - datetime.timedelta(1)
        self.today = timezone.now()
        self.tomorrow = timezone.now() + datetime.timedelta(1)

    def scenario1(self):
        self.publication.publication_start_date = self.today
        self.publication.publication_end_date = self.tomorrow

    def scenario2(self):
        self.publication.publication_start_date = self.tomorrow
        self.publication.publication_end_date = self.today

    def scenario3(self):
        self.publication.publication_start_date = self.today
        self.publication.publication_end_date = self.yesterday

    def scenario4(self):
        self.publication.publication_start_date = self.yesterday
        self.publication.publication_end_date = self.yesterday

    def check_publish_state(self):
        self.publication.publish()
        return self.publication.publication_start_date <= timezone.now() and not self.publication.publication_end_date

    def check_unpublish_state(self):
        self.publication.unpublish()
        return self.publication.publication_start_date <= timezone.now() and self.publication.publication_end_date

    def test_publish(self):
        self.assertTrue(self.publication.is_published())
        self.assertFalse(self.publication.unpublish())
        self.assertTrue(self.publication.publish())
        self.scenario1()
        self.assertTrue(self.check_publish_state())
        self.scenario2()
        self.assertTrue(self.check_publish_state())
        self.scenario3()
        self.assertTrue(self.check_publish_state())
        self.scenario4()
        self.assertTrue(self.check_publish_state())

    def test_unpublish(self):
        self.assertTrue(self.publication.is_published())
        self.assertFalse(self.publication.unpublish())
        self.assertTrue(self.publication.publish())
        self.scenario1()
        self.assertTrue(self.check_unpublish_state())
        self.scenario2()
        self.assertTrue(self.check_unpublish_state())
        self.scenario3()
        self.assertTrue(self.check_unpublish_state())
        self.scenario4()
        self.assertTrue(self.check_unpublish_state())

    def test_is_published(self):
        self.assertTrue(self.publication.is_published())
        self.assertFalse(self.publication.unpublish())
        self.assertFalse(self.publication.is_published())
        self.assertTrue(self.publication.publish())
        self.assertTrue(self.publication.is_published())