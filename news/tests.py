from copy import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application
from publication.test_publication import PublicationAPITestCase


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
        parent_data = copy(response0.data)
        parent_data.update({'parent': parent_data['url'], 'name': 'Category 2'})
        response = self.client.post(self.url, parent_data)
        self.assertEqual(response.data['parent'], parent_data['url'])

