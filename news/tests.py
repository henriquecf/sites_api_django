from copy import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application

from accounts.tests import OwnerGenericTest


class CategoryAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('category-list')
        self.data = {
            'name': 'Category 1',
        }
        self.altered_data = {
            'name': 'Category 1 Altered',
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


class NewsAPITestCase(APILiveServerTestCase):
    def oauth2_authorize(self, username, token, client_type='confidential', grant_type='password'):
        email = '{0}@gmail.com'.format(username)
        self.superuser = User.objects.create(username=username, email=email, password='123')
        aplicacao = Application.objects.create(user=self.superuser, client_type=client_type,
                                               authorization_grant_type=grant_type, client_id=token)
        access_token = AccessToken.objects.create(user=self.superuser, token=token, application=aplicacao,
                                                  expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)

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
        self.oauth2_authorize('user1', '12345')
        super(NewsAPITestCase, self).setUp()

    def test_if_adds_category(self):
        data2 = copy(self.data)
        category_data = {
            'name': 'Category 1',
        }
        category_url = reverse('category-list')
        response = self.client.post(category_url, category_data)
        cat1_url = response.data['url']
        data2.update({'categories': [cat1_url]})
        response2 = self.client.post(self.url, data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['categories'], [cat1_url])