import copy
import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from oauth2_provider.models import Application, AccessToken
from rest_framework import status
from rest_framework.test import APILiveServerTestCase


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
        if self.is_superuser:
            self.user = User.objects.create_superuser(username='firstuser', password='123')
        else:
            self.user = User.objects.create_user(username='firstuser', password='123')
        self.application = Application.objects.create(user=self.user, client_type='confidential',
                                                      authorization_grant_type='password')
        self.username_or_token = self.set_authorization(user=self.user)
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.url = self.test_case.url
        self.first_object_response = self.test_case.client.post(self.url, self.data)

    def set_authorization(self, username='user', random_user=False, user=None):
        if random_user:
            user_number = random.randint(2, 999999)
        else:
            user_number = 1
        new_username = '{0}{1}'.format(username, user_number)
        if user:
            new_user = user
        elif self.is_superuser:
            new_user = User.objects.create_superuser(username=new_username, password='123')
        else:
            new_user = User.objects.create_user(username=new_username, password='123')
        access_token = AccessToken.objects.create(user=new_user, token=new_user.username,
                                                  application=self.application,
                                                  expires=timezone.now() + timedelta(0, 60))
        self.test_case.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
        return access_token.token

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
        self.test_case.assertEqual(response.status_code, status_code, response.data)

    def retrieve(self, status_code=status.HTTP_200_OK):
        response = self.test_case.client.get(self.first_object_response.data['url'])
        self.test_case.assertEqual(response.status_code, status_code)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True):
        response = self.test_case.client.put(self.first_object_response.data['url'], self.altered_data)
        if is_altered:
            self.test_case.assertNotEqual(self.first_object_response.data, response.data)
        self.test_case.assertEqual(response.status_code, status_code, response.data)

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


class UserGenericTest(APIGenericTest):

    def __init__(self, test_case, initial_user_is_superuser=False):
        self.test_case = test_case
        self.is_superuser = initial_user_is_superuser
        if self.is_superuser:
            self.user = User.objects.create_superuser(username='firstuser', password='123')
        else:
            self.user = User.objects.create_user(username='firstuser', password='123')
        self.application = Application.objects.create(user=self.user, client_type='confidential',
                                                      authorization_grant_type='password')
        self.username_or_token = self.set_authorization(user=self.user)
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.url = self.test_case.url
        self.alter_username()
        self.first_object_response = self.test_case.client.post(self.url, self.data)
        self.children_user = User.objects.get(username=self.first_object_response.data['username'])

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
        self.set_authorization(user=self.children_user)
        self.alter_username()
        super(UserGenericTest, self).create(status_code=status.HTTP_403_FORBIDDEN)
        self.reset_authorization()

    def update(self, status_code=status.HTTP_200_OK, is_altered=True):
        self.set_authorization(random_user=True)
        super(UserGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=False)
        self.set_authorization(user=self.children_user)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).update(status_code=status_code, is_altered=is_altered)
        self.alter_username(altered_data=True)
        self.reset_authorization()
        super(UserGenericTest, self).update(status_code=status_code, is_altered=is_altered)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True):
        self.set_authorization(random_user=True)
        super(UserGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.set_authorization(user=self.children_user)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered)
        self.reset_authorization()
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(UserGenericTest, self).list(count=count, status_code=status_code)
        self.alter_username()
        self.test_case.client.post(self.url, self.data)
        super(UserGenericTest, self).list(count=count+1, status_code=status_code)
        self.set_authorization(user=self.children_user)
        super(UserGenericTest, self).list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        self.set_authorization(random_user=True)
        super(UserGenericTest, self).list(count=1, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK):
        super(UserGenericTest, self).retrieve(status_code=status_code)
        self.set_authorization(random_user=True)
        super(UserGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization(user=self.children_user)
        super(UserGenericTest, self).retrieve(status_code=status_code)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT):
        self.set_authorization(random_user=True)
        super(UserGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization(user=self.children_user)
        super(UserGenericTest, self).destroy(status_code=status_code)


# TODO Create tests for children
# TODO Test filters for retriving just children
class UserAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('user-list')
        self.data = {
            'username': 'children',
            'password': '123',
            'email': 'children@email.com',
        }
        self.altered_data = {
            'username': 'childrenaltered',
            'password': '123altered',
            'email': 'childrenaltered@email.com',
        }
        self.user_generic_test = UserGenericTest(self)

    def test_created_user_password(self):
        user = User.objects.get(username=self.user_generic_test.first_object_response.data['username'])
        self.assertNotEqual(user.password, self.data['password'], 'Password is being stored raw')

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

    def test_search_fields(self):
        search_fields = ['username', 'email']
        self.user_generic_test.search_fields(search_fields)
