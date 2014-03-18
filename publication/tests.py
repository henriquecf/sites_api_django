import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import Application, AccessToken
from accounts.tests import OwnerGenericTest, oauth2_authorize


class PublicationGenericTest(OwnerGenericTest):

    def slug_is_slugified_title(self, slug_repeat_number=''):
        response = self.create()
        self.test_case.assertEqual(response.data['slug'], slugify(response.data['title']) + slug_repeat_number, 'Slug is not slugified title')

    def slug_is_unique(self):
        self.slug_is_slugified_title()
        self.slug_is_slugified_title(slug_repeat_number='-2')
        self.slug_is_slugified_title(slug_repeat_number='-3')

    def has_author(self):
        oauth2_authorize(self.test_case.client, 'user_author', 'kashdfjhasdf')
        response = self.create()
        self.test_case.assertIn('author', response.data, 'Response has no field "author"')
        self.test_case.assertEqual(response.data['author'], 'user_author', 'Unexpected author name returned')

    def is_published(self):
        response = self.create()
        self.test_case.assertIn('is_published', response.data, 'Response has no field "is_published"')
        return response.data['is_published']

    def is_published_default_true(self):
        is_published = self.is_published()
        self.test_case.assertTrue(is_published, 'Is_published default value must be True')

    def get_action_response(self, action_name, status_code=status.HTTP_200_OK):
        response = self.create()
        action_url = response.data[action_name]
        response = self.test_case.client.get(action_url)
        self.test_case.assertEqual(response.status_code, status_code)
        return response

    def unpublish(self):
        response = self.get_action_response('unpublish')
        self.test_case.assertFalse(response.data['is_published'], 'Is_published return must be False')

    def publish(self):
        response = self.get_action_response('publish')
        self.test_case.assertTrue(response.data['is_published'], 'Is_published return must be True')


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
        self.token = oauth2_authorize(self.client, 'user1', '12345')
        self.publication_generic_tests = PublicationGenericTest(self)
        super(PublicationAPITestCase, self).setUp()

    def test_create(self):
        """
        Ensure we can create a new publication object
        """
        self.publication_generic_tests.create()

    def test_slug_is_slugified_title(self):
        """
        Checks if the slug is generated automatically
        """
        self.publication_generic_tests.slug_is_slugified_title()

    def test_slug_is_unique(self):
        self.publication_generic_tests.slug_is_unique()

    def test_do_not_create_publication_without_authentication(self):
        """
        Ensure we can create a new publication object
        """
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_has_author(self):
        """
        Ensure publication created has author
        """
        self.publication_generic_tests.has_author()

    def test_list(self):
        """
        Posts some publication and retrieves them back, even when not authenticated
        """
        self.publication_generic_tests.list()

    def test_retrive(self):
        """
        Gets a publication list and retrieves the field url from each publication in the list
        """
        self.publication_generic_tests.retrieve()

    def test_update(self):
        """
        Tests if an authenticated user can update a publication
        """
        self.publication_generic_tests.update()

    def test_partial_update(self):
        self.publication_generic_tests.partial_update()

    def test_unauthenticated_user_can_not_update_publication(self):
        response = self.client.post(self.url, self.data, format='json')
        self.client.credentials()
        altered_data = response.data
        altered_data['title'] = 'Altered title'
        response2 = self.client.patch(altered_data['url'], altered_data)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy(self):
        self.publication_generic_tests.destroy()

    def test_unauthenticated_user_can_not_delete_publication(self):
        response = self.client.post(self.url, self.data, format='json')
        self.client.credentials()
        detail_url = response.data['url']
        response2 = self.client.delete(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_published_default_true(self):
        self.publication_generic_tests.is_published_default_true()

    def test_publish(self):
        self.publication_generic_tests.publish()

    def test_unpublish(self):
        self.publication_generic_tests.unpublish()

    def test_if_non_owner_cannot_access_others_data(self):
        response = self.client.post(self.url, self.data)
        pub_url = response.data['url']
        oauth2_authorize(self.client, 'user2', '123456')
        response2 = self.client.get(pub_url)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_list_retrieves_just_owner_data(self):
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
        oauth2_authorize(self.client, 'user2', '123456')
        response2 = self.client.get(self.url)
        self.assertEqual(response2.data['count'], 0)

    def filter_request(self, field, value):
        filter_data = {
            field: value,
        }
        response_filter = self.client.get(self.url, filter_data)
        self.assertEqual(response_filter.data['count'], 1, 'Did not filter if count = 2')

    def test_if_filter_works(self):
        self.client.post(self.url, self.data)
        data2 = copy.copy(self.data)
        data2.update({
            'title': 'Publication for filter',
            'description': 'Description for filter',
            'publication_start_date': timezone.now() - timedelta(1),
            'publication_end_date': timezone.now() + timedelta(100),
        })
        response = self.client.post(self.url, data2)
        self.filter_request('search', 'filter')
        self.filter_request('title', data2['title'])
        self.filter_request('description', data2['description'])
        # TODO Check filter for datetime fields
        #self.filter_request('publication_start_date', response.data['publication_start_date'])
        #self.filter_request('publication_end_date', response.data['publication_end_date'])
        oauth2_authorize(self.client, 'user2', '1828283')
        self.client.post(self.url, self.data)
        data3 = copy.copy(self.data)
        data3.update({
            'author': 1
        })
        self.client.post(self.url, self.data)
        #self.filter_request('author__username', 'user2')

    # TODO create tests for ordering and pagination in publication