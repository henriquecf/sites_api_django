import copy
import datetime
from datetime import timedelta
from django.test import LiveServerTestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import random
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from resource.test import APIGenericTest
from oauth2_provider.models import AccessToken, Application
from .models import Account, AccountGroup, AccountUser


class AccountAPIGenericTest(APIGenericTest):

    def make_initial_data(self):
        User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
        owner = User.objects.create_user('owner', 'owner@owner.com', '123')
        owner.is_staff = True
        owner.save()
        second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
        second_owner.is_staff = True
        second_owner.save()
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


class AccountAPITestCase(APILiveServerTestCase):
    model = Account

    def setUp(self):
        self.url = reverse('account-list')
        self.data = {}
        self.altered_data = {}
        self.account_api_generic_test = AccountAPIGenericTest(self)

    def test_create(self):
        self.account_api_generic_test.test_create(status_code=status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.account_api_generic_test.test_update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        self.account_api_generic_test.test_partial_update(status_code=status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        self.account_api_generic_test.test_retrieve()

    def test_list(self):
        self.account_api_generic_test.test_list()

    def test_destroy(self):
        self.account_api_generic_test.test_destroy()

    def test_admin_permission(self):
        self.account_api_generic_test.test_admin_permission()

    def test_hyperlinked_fields(self):
        accountuser_url = reverse('accountuser-list')
        response = self.client.post(accountuser_url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.account_api_generic_test.test_serializer_hyperlinked_fields(['owner'])

    def test_default_expiration_date(self):
        self.assertEqual(self.account_api_generic_test.first_object_response.data['expiration_date'],
                         datetime.date.today() + datetime.timedelta(30))

    def test_model_has_custom_permission(self):
        self.account_api_generic_test.test_model_has_custom_permission()

    def test_serializer_read_only_fields(self):
        fields = ['owner']
        self.account_api_generic_test.test_serializer_read_only_fields(fields)


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

    def test_search_fields(self, search_fields=None):
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

    def test_create(self, status_code=status.HTTP_201_CREATED):
        self.alter_username()
        super(UserGenericTest, self).test_create(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        self.alter_username()
        super(UserGenericTest, self).test_create(status_code=status_code)

    def test_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).test_update(status_code=status.HTTP_201_CREATED, is_altered=False, url=url)
        self.alter_username(altered_data=True)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).test_update(status_code=status_code, is_altered=is_altered, url=url)

    def test_partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).test_partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.set_authorization_bearer(self.owner_token)
        self.alter_username(altered_data=True)
        super(UserGenericTest, self).test_partial_update(status_code=status_code, is_altered=is_altered)

    def test_list(self, count=1, status_code=status.HTTP_200_OK):
        super(UserGenericTest, self).test_list(count=count, status_code=status_code)
        self.alter_username()
        self.test_case.client.post(self.url, self.data)
        super(UserGenericTest, self).test_list(count=count+1, status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).test_list(count=1, status_code=status_code)

    def test_retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(UserGenericTest, self).test_retrieve(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).test_retrieve(status_code=status.HTTP_404_NOT_FOUND)

    def test_destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(UserGenericTest, self).test_destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization_bearer(self.owner_token)
        super(UserGenericTest, self).test_destroy(status_code=status_code)


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
        self.user_generic_test.test_create()

    def test_update(self):
        self.user_generic_test.test_update()

    def test_partial_update(self):
        self.user_generic_test.test_partial_update()

    def test_list(self):
        self.user_generic_test.test_list(count=4)

    def test_retrieve(self):
        self.user_generic_test.test_retrieve()

    def test_destroy(self):
        self.user_generic_test.test_destroy()

    def test_admin_permission(self):
        self.user_generic_test.test_admin_permission()

    def test_search_fields(self):
        search_fields = ['username', 'email']
        self.user_generic_test.test_search_fields(search_fields)

    def test_hashed_password(self):
        self.assertNotEqual(self.user_generic_test.first_object_response.data['password'], self.data['password'])

    def test_excluded_serializer_fields(self):
        self.assertNotIn('is_superuser', self.user_generic_test.first_object_response.data)
        response = self.client.get(self.user_generic_test.first_object_response.data['url'])
        self.assertNotIn('password', response.data)

    def test_hyperlinked_fields(self):
        self.user_generic_test.test_serializer_hyperlinked_fields(['accountuser', 'user_permissions', 'groups'])

    def test_accountuser_created_has_same_account_as_request_user(self):
        account_user_url = self.user_generic_test.first_object_response.data['accountuser']
        response = self.client.get(account_user_url)
        account_url = response.data['account']
        account_id = account_url.split('/')[-2]
        owner_account_id = User.objects.get(username=self.user_generic_test.owner_token).accountuser.account.id
        self.assertEqual(account_id, str(owner_account_id))

    def test_serializer_read_only_fields(self):
        fields = ['accountuser']
        self.user_generic_test.test_serializer_read_only_fields(fields)


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

    def test_create(self, status_code=status.HTTP_400_BAD_REQUEST):
        super(AccountUserGenericTest, self).test_create(status_code=status_code)

    def test_update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).test_update(status_code=status_code, is_altered=is_altered, url=url)

    def test_partial_update(self, status_code=status.HTTP_400_BAD_REQUEST, is_altered=False, url=None):
        super(AccountUserGenericTest, self).test_partial_update(status_code=status_code, is_altered=is_altered, url=url)


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
        self.accountuser_generic_test.test_create()

    def test_list(self):
        self.accountuser_generic_test.test_list()

    def test_retrieve(self):
        self.accountuser_generic_test.test_retrieve()

    def test_update(self):
        self.accountuser_generic_test.test_update()

    def test_partial_update(self):
        self.accountuser_generic_test.test_partial_update()

    def test_destroy(self):
        self.accountuser_generic_test.test_destroy()

    def test_admin_permission(self):
        self.accountuser_generic_test.test_admin_permission()

    def test_accountuser_created_has_same_account_as_request_user(self):
        owner_user = User.objects.get(username=self.accountuser_generic_test.owner_token)
        url = self.accountuser_generic_test.first_object_response.data['account']
        account_id = url.split('/')[-2]
        self.assertEqual(account_id, str(owner_user.accountuser.account.id))

    def test_hyperlinked_identity_field(self):
        fields = ['user', 'account']
        self.accountuser_generic_test.test_serializer_hyperlinked_fields(fields)

    def test_model_has_custom_permission(self):
        self.accountuser_generic_test.test_model_has_custom_permission()

    def test_serializer_read_only_fields(self):
        fields = ['user', 'account']
        self.accountuser_generic_test.test_serializer_read_only_fields(fields)


class AccountGroupAPIGenericTest(APIGenericTest):

    def alter_data(self, altered_data=False):
        if not altered_data:
            self.data.update({'role': 'Group {0}'.format(random.randint(1, 100000))})
        else:
            self.altered_data.update({'role': 'Group {0}'.format(random.randint(1, 100000))})

    def test_create(self, status_code=status.HTTP_201_CREATED):
        self.alter_data()
        super(AccountGroupAPIGenericTest, self).test_create(status_code=status_code)

    def test_list(self, count=1, status_code=status.HTTP_200_OK):
        super(AccountGroupAPIGenericTest, self).test_list(count=count, status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(AccountGroupAPIGenericTest, self).test_list(count=0, status_code=status_code)

    def test_retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(AccountGroupAPIGenericTest, self).test_retrieve(status_code=status_code, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(AccountGroupAPIGenericTest, self).test_retrieve(status_code=status.HTTP_404_NOT_FOUND, url=url)

    def test_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(AccountGroupAPIGenericTest, self).test_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(AccountGroupAPIGenericTest, self).test_update(status_code=status.HTTP_201_CREATED, is_altered=True, url=url)

    def test_partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(AccountGroupAPIGenericTest, self).test_partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(AccountGroupAPIGenericTest, self).test_partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False,
                                                               url=url)

    def test_destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(AccountGroupAPIGenericTest, self).test_destroy(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.set_authorization_bearer(self.owner_token)
        super(AccountGroupAPIGenericTest, self).test_destroy(status_code=status_code, url=url)


class GroupAPITestCase(APILiveServerTestCase):
    """Specify the Group's functionality.

    Key features being tested:

    Create, update, partial update, destroy, list and retrieve;
    Admin Permission, Filter groups by account.
    """
    model = AccountGroup

    def setUp(self):
        self.url = reverse('accountgroup-list')
        self.data = {
            'role': 'Group 1',
        }
        self.altered_data = {
            'role': 'Group 1 altered',
        }
        self.account_group_api_generic_test = AccountGroupAPIGenericTest(self)

    def test_create(self):
        self.account_group_api_generic_test.test_create()

    def test_update(self):
        self.account_group_api_generic_test.test_update()

    def test_partial_update(self):
        self.account_group_api_generic_test.test_partial_update()

    def test_retrieve(self):
        self.account_group_api_generic_test.test_retrieve()

    def test_list(self):
        self.account_group_api_generic_test.test_list()

    def test_destroy(self):
        self.account_group_api_generic_test.test_destroy()

    def test_admin_permission(self):
        self.account_group_api_generic_test.test_admin_permission()

    def test_search_fields(self):
        fields = ['role']
        self.account_group_api_generic_test.test_search_fields(fields)

    def test_role_and_account_are_unique_together(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Should not be possible to create another account group with same role name')

    def test_hyperlinked_fields(self):
        fields = ['account']
        self.account_group_api_generic_test.test_serializer_hyperlinked_fields(fields)

    def test_serializer_read_only_fields(self):
        fields = ['account', 'name']
        self.account_group_api_generic_test.test_serializer_read_only_fields(fields)