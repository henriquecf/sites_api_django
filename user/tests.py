import copy
import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from oauth2_provider.models import Application, AccessToken
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from accounts.models import Account
from user.models import AccountUser


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


class UserGenericTest(APIGenericTest):

    def alter_username(self, altered_data=False):
        username = 'user-{0}'.format(random.randint(1, 999999))
        if altered_data:
            data = self.altered_data
        else:
            data = self.data
        data.update({
            'username': username,
        })

    def search_fields(self, search_fields=None):
        for field in search_fields:
            filter_parameter = random.randint(1, 999999)
            self.altered_data.update({'username': filter_parameter + 1})
            if field == 'email':
                filter_parameter = '{0}@gm.com'.format(filter_parameter)
            self.altered_data.update({field: filter_parameter})
            self.test_case.client.post(self.url, self.altered_data)
            query_parameter = {'search': filter_parameter}
            response = self.test_case.client.get(self.url, query_parameter)
            self.test_case.assertEqual(response.data['count'], 1, 'Field "{0}" not in search fields'.format(field))

    def create(self, status_code=status.HTTP_201_CREATED):
        self.alter_username()
        super(UserGenericTest, self).create(status_code=status_code)
        self.set_authorization_bearer(self.account_user_token)
        self.alter_username()
        super(UserGenericTest, self).create(status_code=status.HTTP_403_FORBIDDEN)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=False, url=url)
        self.set_authorization_bearer(self.account_user_token)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).update(status_code=status_code, is_altered=is_altered)
        self.alter_username(altered_data=True)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).update(status_code=status_code, is_altered=is_altered)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.set_authorization_bearer(self.account_user_token)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered)
        self.set_authorization_bearer(self.owner_token)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(UserGenericTest, self).list(count=count, status_code=status_code)
        self.alter_username()
        self.test_case.client.post(self.url, self.data)
        super(UserGenericTest, self).list(count=count+1, status_code=status_code)
        self.set_authorization_bearer(self.account_user_token)
        super(UserGenericTest, self).list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).list(count=1, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(UserGenericTest, self).retrieve(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization_bearer(self.account_user_token)
        super(UserGenericTest, self).retrieve(status_code=status_code)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization_bearer(self.account_user_token)
        super(UserGenericTest, self).destroy(status_code=status_code)


# TODO Create tests for children
# TODO Test filters for retriving just children
class UserAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('accountuser-list')
        self.data = {
        }
        self.altered_data = {
        }
        self.user_generic_test = UserGenericTest(self)

    def test_required_email(self):
        data = copy.copy(self.data)
        data.pop('email')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create(self):
        self.user_generic_test.create()

    def test_update(self):
        self.user_generic_test.update()

    def test_partial_update(self):
        self.user_generic_test.partial_update()

    def test_list(self):
        self.user_generic_test.list(count=2)

    def test_retrieve(self):
        self.user_generic_test.retrieve()

    def test_destroy(self):
        self.user_generic_test.destroy()
