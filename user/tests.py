import copy
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from oauth2_provider.models import Application, AccessToken
import random
from rest_framework import status
from rest_framework.test import APILiveServerTestCase


def oauth2_authorize(client, username_and_token, client_type='confidential', grant_type='password', is_superuser=False):
    email = '{0}@gmail.com'.format(username_and_token)
    if is_superuser:
        user = User.objects.create_superuser(username=username_and_token, email=email, password='123')
    else:
        user = User.objects.create_user(username=username_and_token, email=email, password='123')
    aplicacao = Application.objects.create(user=user, client_type=client_type, authorization_grant_type=grant_type,
                                           client_id=username_and_token)
    access_token = AccessToken.objects.create(user=user, token=username_and_token, application=aplicacao,
                                              expires=timezone.now() + timedelta(0, 60))
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
    return access_token.token


class APIGenericTest:
    """
    Generic tests for django rest framework api tests.
    Tests create, update, retrieve, list, partial update, destroy actions
    This class should be instanced inside the TestCase,
    passing the own TestCase as a parameter
    """

    def __init__(self, test_case, initial_user_is_superuser=False):
        self.test_case = test_case
        self.is_superuser = initial_user_is_superuser
        self.username_or_token = self.set_authorization()
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.url = self.test_case.url
        data = copy.copy(self.data)
        try:
            data['username'] = 'user'
        except KeyError:
            pass
        self.first_object_response = self.test_case.client.post(self.url, data)

    def set_authorization(self, username='user', random_user=False):
        if random_user:
            user_number = random.randint(2, 999999)
        else:
            user_number = 1
        new_username = '{0}{1}'.format(username, user_number)
        oauth2_authorize(self.test_case.client, username_and_token=new_username, is_superuser=self.is_superuser)
        return new_username

    def reset_authorization(self, token=None):
        if not token:
            token = self.username_or_token
        self.test_case.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def create(self, status_code=status.HTTP_201_CREATED):
        response = self.test_case.client.post(self.url, self.data)
        self.test_case.assertEqual(response.status_code, status_code, response.data)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        response = self.test_case.client.get(self.url)
        if count >= 0:
            self.test_case.assertEqual(response.data['count'], count)
        self.test_case.assertEqual(response.status_code, status_code)

    def retrieve(self, status_code=status.HTTP_200_OK):
        response = self.test_case.client.get(self.first_object_response.data['url'])
        self.test_case.assertEqual(response.status_code, status_code)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True):
        response = self.test_case.client.put(self.first_object_response.data['url'], self.altered_data)
        if is_altered:
            self.test_case.assertNotEqual(self.first_object_response.data, response.data)
        self.test_case.assertEqual(response.status_code, status_code)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True):
        response = self.test_case.client.patch(self.first_object_response.data['url'], self.altered_data)
        if is_altered:
            self.test_case.assertNotEqual(self.first_object_response.data, response.data)
        self.test_case.assertEqual(response.status_code, status_code)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT):
        response = self.test_case.client.delete(self.first_object_response.data['url'])
        self.test_case.assertEqual(response.status_code, status_code)

    def search_fields(self, search_fields=None):
        for field in search_fields:
            filter_parameter = random.randint(1, 999999)
            self.altered_data.update({field: filter_parameter})
            self.test_case.client.post(self.url, self.altered_data)
            query_parameter = {'search': filter_parameter}
            response = self.test_case.client.get(self.url, query_parameter)
            self.test_case.assertEqual(response.data['count'], 1, 'Field "{0}" not in search fields'.format(field))

    # TODO Still need to create a generic test for ordering


class ChildrenGenericTest(APIGenericTest):

    def create_children(self):
        data = {
            'username': 'children',
            'password': '123',
        }
        url = reverse('user-list')
        response = self.test_case.client.post(url, data)
        self.test_case.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def create(self, status_code=status.HTTP_201_CREATED):
        super(ChildrenGenericTest, self).create(status_code=status_code)


class UserAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('user-list')
        self.data = {
            'username': 'children',
            'password': '123',
        }
        self.altered_data = {
            'username': 'childrenaltered',
            'password': '123altered',
        }
        self.api_generic_test = APIGenericTest(self)

    def test_created_user_password(self):
        user = User.objects.get(username='user')
        print(self.data, user.password, user.username)
        self.assertNotEqual(user.password, self.data['password'], 'Password is being stored raw')

    def test_create(self):
        self.api_generic_test.create()
