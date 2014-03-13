from copy import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.files import File
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application
from publication.test_publication import PublicationAPITestCase
from .models import News


class CategoryAPITestCase(APILiveServerTestCase):
    url = reverse('category-list')
    data = {
        'name': 'Category 1',
    }

    def oauth2_authorize(self, username, token, client_type='confidential', grant_type='password'):
        email = '{0}@gmail.com'.format(username)
        self.superuser = User.objects.create(username=username, email=email, password='123')
        aplicacao = Application.objects.create(user=self.superuser, client_type=client_type, authorization_grant_type=grant_type, client_id=token)
        access_token = AccessToken.objects.create(user=self.superuser, token=token, application=aplicacao, expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)

    def setUp(self):
        self.oauth2_authorize(username='user1', token='12345')
        super(CategoryAPITestCase, self).setUp()

    def test_cant_list_without_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_lists_when_authenticated(self):
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_if_creates(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_if_retrieves_url(self):
        response = self.client.post(self.url, self.data)
        detail_url = response.data['url']
        response2 = self.client.get(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_if_updates(self):
        response = self.client.post(self.url, self.data)
        data = response.data
        new_name = 'Updated Category 1'
        data['name'] = new_name
        response2 = self.client.patch(response.data['url'], data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['name'], new_name)

    def test_if_deletes(self):
        response = self.client.post(self.url, self.data)
        response2 = self.client.delete(response.data['url'])
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)

    def test_if_creates_with_parent(self):
        response0 = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response0.data['url'], 'name': 'Category 2'})
        response = self.client.post(self.url, children_data)
        self.assertEqual(response.data['parent'], response0.data['url'])

    def test_if_lists_just_owner_items(self):
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
        self.oauth2_authorize(username='user2', token='123456')
        response2 = self.client.get(self.url)
        self.assertEqual(response2.data['count'], 0)
        self.assertEqual(response2.data['results'], [])

    def test_if_gets_descendants(self):
        response0 = self.client.post(self.url, self.data)
        children_data = copy(self.data)
        children_data.update({'parent': response0.data['url'], 'name': 'Category 2'})
        response = self.client.post(self.url, children_data)
        response1 = self.client.get(response0.data['url'])
        self.assertIn('get_descendants', response1.data)
        get_descendants_url = response1.data['get_descendants']
        response2 = self.client.get(get_descendants_url)
        self.assertEqual(response2.data['descendants'][0], response.data)

    def test_if_has_is_leaf_node_field(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('is_leaf_node', response.data)
        self.assertTrue(response.data['is_leaf_node'])
        children_data = copy(self.data)
        children_data.update({'parent': response.data['url'], 'name': 'Category 2'})
        self.client.post(self.url, children_data)
        response2 = self.client.get(response.data['url'])
        self.assertFalse(response2.data['is_leaf_node'])


class NewsAPITestCase(PublicationAPITestCase):

    def setUp(self):
        super(NewsAPITestCase, self).setUp()
        self.url = reverse('news-list')
        self.data.update({'content': 'My first news', 'title': 'My first news'})

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

    # TODO Do filters for news and category