import copy
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
import random

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from resource.tests import APIGenericTest, TestDataMixin
from publication.settings import os, BASE_DIR


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

    def admin_permission(self):
        self.set_authorization_bearer(self.account_user_token)
        super(UserGenericTest, self).create(status_code=status.HTTP_403_FORBIDDEN)
        super(UserGenericTest, self).update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False)
        super(UserGenericTest, self).partial_update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False)
        super(UserGenericTest, self).list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        super(UserGenericTest, self).retrieve(status_code=status.HTTP_403_FORBIDDEN)
        super(UserGenericTest, self).destroy(status_code=status.HTTP_403_FORBIDDEN)

    def create(self, status_code=status.HTTP_201_CREATED):
        self.alter_username()
        super(UserGenericTest, self).create(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        self.alter_username()
        super(UserGenericTest, self).create(status_code=status_code)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=False, url=url)
        self.alter_username(altered_data=True)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.set_authorization_bearer(self.owner_token)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(UserGenericTest, self).list(count=count, status_code=status_code)
        self.alter_username()
        self.test_case.client.post(self.url, self.data)
        super(UserGenericTest, self).list(count=count+1, status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).list(count=4, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(UserGenericTest, self).retrieve(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).destroy(status_code=status_code)


class UserAPITestCase(APILiveServerTestCase, TestDataMixin):

    def setUp(self):
        self.url = reverse('user-list')
        self.data = {
            'username': 'another_user',
            'password': '123',
            'email': 'another_user@email.com',
        }
        self.altered_data = {
            'username': 'another_user_altered',
            'password': '123altered',
            'email': 'another_user_altered@email.com',
        }
        self.user_generic_test = UserGenericTest(self)

    def test_required_email(self):
        data = copy.copy(self.data)
        data.pop('email')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_create(self):
        self.user_generic_test.create()

    def test_update(self):
        self.user_generic_test.update()

    def test_partial_update(self):
        self.user_generic_test.partial_update()

    def test_list(self):
        self.user_generic_test.list(count=5)

    def test_retrieve(self):
        self.user_generic_test.retrieve()

    def test_destroy(self):
        self.user_generic_test.destroy()

    def test_admin_permission(self):
        self.user_generic_test.admin_permission()

    def test_search_fields(self):
        search_fields = ['username', 'email']
        self.user_generic_test.search_fields(search_fields)

    def test_hashed_password(self):
        self.assertNotEqual(self.user_generic_test.first_object_response.data['password'], self.data['password'])

    def test_user_viewset_get_serializer(self):
        self.user_generic_test.alter_username()
        response = self.client.post(self.url, self.data)
        self.assertNotIn('is_active', response.data)
        self.user_generic_test.alter_username(altered_data=True)
        response2 = self.client.patch(response.data['url'], self.altered_data)
        self.assertNotIn('is_active', response2.data)
        response3 = self.client.get(response.data['url'])
        self.assertIn('is_active', response3.data)
        response4 = self.client.get(self.url)
        self.assertIn('is_active', response4.data['results'][0])

    # TODO Check why this test is not passing
    '''def test_accountuser_created_has_same_account_as_request_user(self):
        response = self.client.get(self.user_generic_test.first_object_response.data['accountuser'])
        owner_user = User.objects.get(username=self.user_generic_test.owner_token)
        self.assertEqual(response.data['account'], owner_user.accountuser.account)'''


class AccountUserGenericTest(APIGenericTest):

    def create(self, status_code=status.HTTP_400_BAD_REQUEST):
        super(AccountUserGenericTest, self).create(status_code=status_code)

    def update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)


class AccountUserTestCase(APILiveServerTestCase):
    fixtures = [os.path.join(BASE_DIR, 'user/test_data.json')]

    def setUp(self):
        self.url = reverse('accountuser-list')
        self.data = {
        }
        self.altered_data = {
        }
        self.accountuser_generic_test = AccountUserGenericTest(self)

    def test_create(self):
        self.accountuser_generic_test.create()

    def test_list(self):
        self.accountuser_generic_test.list()

    def test_retrieve(self):
        self.accountuser_generic_test.retrieve()

    def test_update(self):
        self.accountuser_generic_test.update()

    def test_partial_update(self):
        self.accountuser_generic_test.partial_update()

    def test_destroy(self):
        self.accountuser_generic_test.destroy()


class UserTestCase(LiveServerTestCase, TestDataMixin):

    def test_user_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'henrique',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)