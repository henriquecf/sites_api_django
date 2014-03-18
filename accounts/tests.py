import copy
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import AccessToken, Application
from accounts.models import Common, Owner


def oauth2_authorize(client, username, token, client_type='confidential', grant_type='password', is_superuser=False):
    email = '{0}@gmail.com'.format(username)
    if is_superuser:
        user = User.objects.create_superuser(username=username, email=email, password='123')
    else:
        user = User.objects.create_user(username=username, email=email, password='123')
    aplicacao = Application.objects.create(user=user, client_type=client_type, authorization_grant_type=grant_type, client_id=token)
    access_token = AccessToken.objects.create(user=user, token=token, application=aplicacao, expires=timezone.now() + timedelta(0, 60))
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
    return access_token.token


def reset_authorization(client, token):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)


class APIGenericTest:
    """
    Generic tests for django rest framework api tests.
    Tests create, update, retrieve, list, partial update, destroy actions
    This class should be instanced inside the TestCase,
    passing the own TestCase as a parameter
    """
    def __init__(self, test_case):
        self.test_case = test_case

    def create(self, authorized=True):
        if authorized:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_401_UNAUTHORIZED
        response = self.test_case.client.post(self.test_case.url, self.test_case.data)
        self.test_case.assertEqual(response.status_code, status_code)
        return response

    def list(self, count=0):
        response = self.test_case.client.get(self.test_case.url)
        self.test_case.assertEqual(response.data['count'], count)
        self.create()
        response2 = self.test_case.client.get(self.test_case.url)
        self.test_case.assertEqual(response2.data['count'], count + 1)

    def retrieve(self):
        response = self.create()
        response2 = self.test_case.client.get(response.data['url'])
        self.test_case.assertEqual(response2.status_code, status.HTTP_200_OK)
        return response

    def update(self, authorized=True):
        if authorized:
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_401_UNAUTHORIZED
        response = self.create(authorized=authorized)
        response2 = self.test_case.client.put(response.data['url'], self.test_case.altered_data)
        self.test_case.assertNotEqual(response.data, response2.data)
        self.test_case.assertEqual(response2.status_code, status_code)

    def partial_update(self):
        response = self.create()
        response2 = self.test_case.client.patch(response.data['url'], self.test_case.altered_data)
        self.test_case.assertNotEqual(response.data, response2.data)
        self.test_case.assertEqual(response2.status_code, status.HTTP_200_OK)

    def destroy(self):
        response = self.create()
        response2 = self.test_case.client.delete(response.data['url'])
        self.test_case.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)


class OwnerGenericTest(APIGenericTest):

    def create(self, authorized=True):
        response = super(OwnerGenericTest, self).create(authorized=authorized)
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).create(authorized=False)
        reset_authorization(self.test_case.client, self.test_case.token)
        return response

    def update(self, authorized=True):
        super(OwnerGenericTest, self).update()
        self.test_case.client.credentials()
        super(OwnerGenericTest, self).update(authorized=False)
        reset_authorization(self.test_case.client, self.test_case.token)

    def owner_is_request_user(self, is_superuser=False):
        oauth2_authorize(self.test_case.client, 'owner_user', 'dnsajndjksndjpofdaas', is_superuser=is_superuser)
        response = self.create()
        owner_id = response.data['url'].split('/')[-2]
        owner_model = Owner.objects.get(id=owner_id)
        owner_user = User.objects.get(username='owner_user')
        self.test_case.assertEqual(owner_user, owner_model.owner)

    def just_owner_can_access_its_data(self, is_superuser=False):
        response = self.retrieve()
        oauth2_authorize(self.test_case.client, 'other_user', 'hfsjal93u3285yrhlwdk', is_superuser=is_superuser)
        response2 = self.test_case.client.get(response.data['url'])
        self.test_case.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)


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
        data = ({
            'username': 'henrique',
            'email': 'elo.henrique@gmail.com',
            'password1': '123',
            'password2': '123',
        })
        url = reverse('user-create')
        self.client.post(url, data)
        new_users_count = User.objects.count()
        self.assertEqual(users_count + 1, new_users_count, 'User was not created: {0}'.format(data))
        data.update({'username': 'ivan', 'email': ''})
        self.client.post(url, data)
        second_users_count = User.objects.count()
        self.assertEqual(new_users_count, second_users_count, 'User without email should not be created: {0}'.format(data))

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
        self.data = {

        }
        self.altered_data = {

        }
        self.token = oauth2_authorize(self.client, 'superuser', '12345', is_superuser=True)
        self.owner_generic_tests = OwnerGenericTest(self)

    def test_if_can_not_access_create_account_without_login(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_any_user_can_access_data(self):
        oauth2_authorize(self.client, 'user', '123456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        self.owner_generic_tests.create()

    def test_list(self):
        self.owner_generic_tests.list()

    def test_retrieve(self):
        self.owner_generic_tests.retrieve()

    def test_update(self):
        self.owner_generic_tests.update()

    def test_partial_update(self):
        self.owner_generic_tests.partial_update()

    def test_destroy(self):
        self.owner_generic_tests.destroy()

    def test_owner_is_request_user(self):
        self.owner_generic_tests.owner_is_request_user(is_superuser=True)

    def test_just_owner_can_access_its_data(self):
        self.owner_generic_tests.just_owner_can_access_its_data(is_superuser=True)


# TODO Create tests to create app user, test if just owner and children access data