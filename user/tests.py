import copy
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
import random

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from resource.tests import APIGenericTest
from oauth2_provider.models import AccessToken, Application
from accounts.models import Account
from .models import AccountUser


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
        super(UserGenericTest, self).list(count=1, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(UserGenericTest, self).retrieve(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).destroy(status_code=status_code)


class UserAPITestCase(APILiveServerTestCase):
    model = User

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
        self.user_generic_test.list(count=3)

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

    def test_hyperlinked_fields(self):
        self.user_generic_test.hyperlinked_fields(['accountuser'])

    def test_accountuser_created_has_same_account_as_request_user(self):
        account_user_url = self.user_generic_test.first_object_response.data['accountuser']
        response = self.client.get(account_user_url)
        account_url = response.data['account']
        account_id = account_url.split('/')[-2]
        owner_account_id = User.objects.get(username=self.user_generic_test.owner_token).accountuser.account.id
        self.assertEqual(account_id, str(owner_account_id))


class AccountUserGenericTest(APIGenericTest):

    def make_initial_data(self):
        User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
        owner = User.objects.create_user('owner', 'owner@owner.com', '123')
        owner.is_staff = True
        owner.save()
        second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
        second_owner.is_staff = True
        second_owner.save()
        owner_account = Account.objects.create(owner=owner)
        second_owner_account = Account.objects.create(owner=second_owner)
        owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
        owner_application = Application.objects.create(user=owner, client_type='confidential',
                                                       authorization_grant_type='password')
        second_owner_application = Application.objects.create(user=second_owner, client_type='confidential',
                                                              authorization_grant_type='password')
        self.owner_token = AccessToken.objects.create(user=owner, token=owner.username, application=owner_application,
                                                      expires=timezone.now() + timedelta(30)).token
        self.second_owner_token = AccessToken.objects.create(user=second_owner, token=second_owner.username,
                                                             application=second_owner_application,
                                                             expires=timezone.now() + timedelta(30)).token
        self.account_user_token = AccessToken.objects.create(user=owner_user, token=owner_user.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token

    def create(self, status_code=status.HTTP_400_BAD_REQUEST):
        super(AccountUserGenericTest, self).create(status_code=status_code)

    def update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)


class AccountUserTestCase(APILiveServerTestCase):
    model = AccountUser

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

    def test_admin_permission(self):
        self.accountuser_generic_test.admin_permission()

    def test_accountuser_created_has_same_account_as_request_user(self):
        owner_user = User.objects.get(username=self.accountuser_generic_test.owner_token)
        url = self.accountuser_generic_test.first_object_response.data['account']
        account_id = url.split('/')[-2]
        self.assertEqual(account_id, str(owner_user.accountuser.account.id))

    def test_hyperlinked_identity_field(self):
        fields = ['user', 'account']
        self.accountuser_generic_test.hyperlinked_fields(fields)

    def test_model_has_custom_permission(self):
        self.accountuser_generic_test.model_has_custom_permission()


class UserTestCase(LiveServerTestCase):

    def setUp(self):
        User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')

    def test_user_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'henrique',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)