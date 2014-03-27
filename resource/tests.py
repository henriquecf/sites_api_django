from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from oauth2_provider.models import AccessToken
import random
from rest_framework import status
from publication.settings import os, BASE_DIR

from resource.models import Resource


class TestDataMixin(object):
    fixtures = [os.path.join(BASE_DIR, 'general_test_data.json')]


class APIGenericTest:
    """
    Generic tests for django rest framework api tests.
    Tests create, update, retrieve, list, partial update, destroy actions
    This class should be instanced inside the TestCase,
    passing the own TestCase as a parameter
    """
    def load_initial_data(self):
        self.owner_token = AccessToken.objects.get(id=1).token
        self.account_user_token = AccessToken.objects.get(id=2).token
        self.account_user_token2 = AccessToken.objects.get(id=3).token
        self.account_user_token3 = AccessToken.objects.get(id=4).token
        self.second_owner_token = AccessToken.objects.get(id=5).token
        self.second_account_user_token = AccessToken.objects.get(id=6).token
        self.second_account_user_token2 = AccessToken.objects.get(id=7).token
        self.second_account_user_token3 = AccessToken.objects.get(id=8).token

    def __init__(self, test_case):
        self.test_case = test_case
        self.url = self.test_case.url
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.load_initial_data()
        self.set_authorization_bearer(self.owner_token)
        self.first_object_response = self.test_case.client.post(self.url, self.data)

    def set_authorization_bearer(self, token):
        self.test_case.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def create(self, status_code=status.HTTP_201_CREATED):
        response = self.test_case.client.post(self.url, self.data)
        self.test_case.assertEqual(response.status_code, status_code, response.data)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        response = self.test_case.client.get(self.url)
        if count >= 0:
            self.test_case.assertEqual(response.data['count'], count)
        self.test_case.assertEqual(response.status_code, status_code, response.data)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        if not url:
            url = self.first_object_response.data['url']
        response = self.test_case.client.get(url)
        self.test_case.assertEqual(response.status_code, status_code)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        if not url:
            url = self.first_object_response.data['url']
        response = self.test_case.client.put(url, self.altered_data)
        if is_altered:
            self.test_case.assertNotEqual(self.first_object_response.data, response.data)
        self.test_case.assertEqual(response.status_code, status_code, response.data)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        if not url:
            url = self.first_object_response.data['url']
        response = self.test_case.client.patch(url, self.altered_data)
        if is_altered:
            self.test_case.assertNotEqual(self.first_object_response.data, response.data)
        self.test_case.assertEqual(response.status_code, status_code)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        if not url:
            url = self.first_object_response.data['url']
        response = self.test_case.client.delete(url)
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


class PermissionGenericTest(APIGenericTest):

    def model_has_custom_permission(self):
        model_name = self.test_case.model._meta.model_name
        view_permission = 'view_{0}'.format(model_name)
        database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename',
                                                                                                    flat=True)
        self.test_case.assertIn(view_permission, database_permissions)


class ResourceGenericTest(PermissionGenericTest):

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False,
                                                        url=url)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(ResourceGenericTest, self).list(count=count, status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).list(count=0, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(ResourceGenericTest, self).retrieve(status_code=status_code, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND, url=url)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).destroy(status_code=status_code, url=url)

    def owner_is_request_user(self):
        self.set_authorization_bearer(self.second_owner_token)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Resource.objects.get(id=owner_id)
        user = User.objects.get(username=self.second_owner_token)
        self.test_case.assertEqual(user, owner_obj.creator)


# TODO This tests must be revised
class UserTestCase(LiveServerTestCase, TestDataMixin):

    def test_user_create_url_exists(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        users_count = User.objects.count()
        data = (dict(username='another_user', email='another_user@gmail.com', password1='123', password2='123'))
        url = reverse('user-create')
        self.client.post(url, data)
        new_users_count = User.objects.count()
        self.assertEqual(users_count + 1, new_users_count, 'User was not created: {0}'.format(data))
        data.update({'username': 'another_user_altered', 'email': ''})
        self.client.post(url, data)
        second_users_count = User.objects.count()
        self.assertEqual(new_users_count, second_users_count,
                         'User without email should not be created: {0}'.format(data))

    def test_user_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'henrique',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)