import copy, datetime
import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application

from accounts.models import Common, Owner


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
        self.first_object_response = self.test_case.client.post(self.url, self.data)

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
        self.test_case.assertEqual(response.status_code, status_code)

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


class OwnerGenericTest(APIGenericTest):
    def create(self, status_code=status.HTTP_201_CREATED):
        response = super(OwnerGenericTest, self).create()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).create(status_code=status.HTTP_401_UNAUTHORIZED)
        self.reset_authorization()
        return response

    def update(self, status_code=status.HTTP_200_OK, is_altered=True):
        super(OwnerGenericTest, self).update()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).update(status_code=status.HTTP_401_UNAUTHORIZED, is_altered=False)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).update(status_code=status.HTTP_201_CREATED)
        self.reset_authorization()

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True):
        super(OwnerGenericTest, self).partial_update()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).partial_update(status_code=status.HTTP_401_UNAUTHORIZED, is_altered=False)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.reset_authorization()

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(OwnerGenericTest, self).list()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).list(count=-1, status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).list(count=0)
        self.reset_authorization()

    def retrieve(self, status_code=status.HTTP_200_OK):
        super(OwnerGenericTest, self).retrieve()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).retrieve(status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        self.reset_authorization()

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT):
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).destroy(status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.reset_authorization()
        super(OwnerGenericTest, self).destroy()

    def owner_is_request_user(self):
        username = self.set_authorization(random_user=True)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Owner.objects.get(id=owner_id)
        user = User.objects.get(username=username)
        self.test_case.assertEqual(user, owner_obj.owner)


class CommonTestCase(LiveServerTestCase):
    def setUp(self):
        self.common = Common.objects.create()

    def test_create_common_fields(self):
        """
        Ensure common is created
        """
        self.assertTrue(self.common.creation_date)
        self.assertTrue(self.common.last_modification_date)

    def test_update_common_fields(self):
        """
        Ensure common field last_modification_date is changed when object is saved
        """
        common2 = copy.copy(self.common)
        self.common.save()
        self.assertNotEqual(self.common.last_modification_date, common2.last_modification_date)


class UserTestCase(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='123', email='user@user.com')

    def test_if_user_create_url_exists(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_creates_user(self):
        users_count = User.objects.count()
        data = (dict(username='henrique', email='elo.henrique@gmail.com', password1='123', password2='123'))
        url = reverse('user-create')
        self.client.post(url, data)
        new_users_count = User.objects.count()
        self.assertEqual(users_count + 1, new_users_count, 'User was not created: {0}'.format(data))
        data.update({'username': 'ivan', 'email': ''})
        self.client.post(url, data)
        second_users_count = User.objects.count()
        self.assertEqual(new_users_count, second_users_count,
                         'User without email should not be created: {0}'.format(data))

    def test_if_user_can_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'user',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)


class AccountAPITestCase(APILiveServerTestCase):
    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        self.owner_generic_test = OwnerGenericTest(self)

    def test_create(self):
        self.owner_generic_test.create()

    def test_list(self):
        self.owner_generic_test.list()

    def test_retrieve(self):
        self.owner_generic_test.retrieve()

    def test_update(self):
        self.owner_generic_test.update()

    def test_partial_update(self):
        self.owner_generic_test.partial_update()

    def test_destroy(self):
        self.owner_generic_test.destroy()

    def test_owner_is_user_request(self):
        self.owner_generic_test.owner_is_request_user()

    def test_default_expiration_date(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.data['expiration_date'], datetime.date.today() + datetime.timedelta(30))