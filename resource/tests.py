from itertools import chain
from datetime import timedelta
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application
import random
from rest_framework import status
from resource.models import Resource
from account.models import Account, AccountUser


class APIGenericTest:
    """
    Generic tests for django rest framework api tests.
    Tests create, update, retrieve, list, partial update, destroy actions
    This class should be instanced inside the TestCase,
    passing the own TestCase as a parameter
    """

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
        AccountUser.objects.create(account=owner_account, user=owner)
        AccountUser.objects.create(account=second_owner_account, user=second_owner)
        owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
        owner_user2 = User.objects.create_user('owner_user2', 'owner_user2@owner.com', '123')
        AccountUser.objects.create(account=owner_account, user=owner_user)
        AccountUser.objects.create(account=owner_account, user=owner_user2)
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
        self.account_user_token2 = AccessToken.objects.create(user=owner_user2,
                                                              token=owner_user2.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token
        self.owner = owner
        self.second_owner = second_owner
        self.account_user = owner_user
        self.account_user2 = owner_user2
        # TODO Take care of permissions dependencies between models.
        # TODO Model inheritance must include permission inheritance.
        model_name = self.test_case.model._meta.model_name
        permissions = Permission.objects.filter(codename__endswith=model_name)
        pub_permissions = Permission.objects.filter(codename__endswith='publication')
        cat_permissions = Permission.objects.filter(codename__endswith='category')
        for permission in chain(permissions, pub_permissions, cat_permissions):
            self.owner.user_permissions.add(permission)
            self.second_owner.user_permissions.add(permission)
            self.account_user2.user_permissions.add(permission)
            self.account_user2.accountuser.global_permissions.add(permission)

    def __init__(self, test_case):
        self.test_case = test_case
        self.url = self.test_case.url
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.make_initial_data()
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

    def admin_permission(self):
        self.set_authorization_bearer(self.account_user_token)
        url = self.first_object_response.data['url']
        response = self.test_case.client.post(self.url, self.data)
        self.test_case.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response2 = self.test_case.client.put(url, self.altered_data)
        self.test_case.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        response3 = self.test_case.client.patch(self.url, self.altered_data)
        self.test_case.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)
        response4 = self.test_case.client.get(self.url)
        self.test_case.assertEqual(response4.status_code, status.HTTP_403_FORBIDDEN)
        response5 = self.test_case.client.get(url)
        self.test_case.assertEqual(response5.status_code, status.HTTP_403_FORBIDDEN)
        response6 = self.test_case.client.delete(url)
        self.test_case.assertEqual(response6.status_code, status.HTTP_403_FORBIDDEN)

    def search_fields(self, search_fields=None):
        for field in search_fields:
            filter_parameter = random.randint(1, 999999)
            self.altered_data.update({field: filter_parameter})
            self.test_case.client.post(self.url, self.altered_data)
            query_parameter = {'search': filter_parameter}
            response = self.test_case.client.get(self.url, query_parameter)
            self.test_case.assertEqual(response.data['count'], 1, 'Field "{0}" not in search fields'.format(field))

            # TODO Still need to create a generic test for ordering

    # TODO Check if this test is really working
    def serializer_hyperlinked_fields(self, fields):
        for field in fields:
            response = self.test_case.client.get(self.first_object_response.data[field])
            self.test_case.assertEqual(response.status_code, status.HTTP_200_OK, 'Error with field {0}'.format(field))

    def model_has_custom_permission(self):
        model_name = self.test_case.model._meta.model_name
        view_permission = 'view_{0}'.format(model_name)
        database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename',
                                                                                                    flat=True)
        self.test_case.assertIn(view_permission, database_permissions)

    def serializer_read_only_fields(self, fields):
        for field in fields:
            response = self.test_case.client.options(self.url)
            self.test_case.assertEqual(True, response.data['actions']['POST'][field]['read_only'])


class ResourceGenericTest(APIGenericTest):
    def create(self, status_code=status.HTTP_201_CREATED):
        super(ResourceGenericTest, self).create(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).create(status_code=status_code)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).create(status_code=status.HTTP_403_FORBIDDEN)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).create(status_code=status.HTTP_403_FORBIDDEN)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False, url=url)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False, url=url)
        self.set_authorization_bearer(self.account_user_token2)
        super(ResourceGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.account_user2.accountuser.global_permissions.clear()
        super(ResourceGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=False, url=url)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False,
                                                        url=url)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False,
                                                        url=url)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False,
                                                        url=url)
        self.set_authorization_bearer(self.account_user_token2)
        super(ResourceGenericTest, self).partial_update(status_code=status_code, is_altered=True, url=url)
        self.account_user2.accountuser.global_permissions.clear()
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False,
                                                        url=url)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(ResourceGenericTest, self).list(count=count, status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).list(count=0, status_code=status_code)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        self.set_authorization_bearer(self.account_user_token2)
        super(ResourceGenericTest, self).list(count=count, status_code=status_code)
        self.account_user2.accountuser.global_permissions.clear()
        super(ResourceGenericTest, self).list(count=0, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(ResourceGenericTest, self).retrieve(status_code=status_code, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).retrieve(status_code=status.HTTP_403_FORBIDDEN, url=url)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).retrieve(status_code=status.HTTP_403_FORBIDDEN, url=url)
        self.set_authorization_bearer(self.account_user_token2)
        super(ResourceGenericTest, self).retrieve(status_code=status_code, url=url)
        self.account_user2.accountuser.global_permissions.clear()
        super(ResourceGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND, url=url)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.set_authorization_bearer(self.account_user_token2)
        super(ResourceGenericTest, self).destroy(status_code=status_code, url=url)
        self.account_user2.accountuser.global_permissions.clear()
        super(ResourceGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.set_authorization_bearer(self.account_user_token)
        super(ResourceGenericTest, self).destroy(status_code=status.HTTP_403_FORBIDDEN, url=url)
        self.owner.user_permissions.clear()
        self.set_authorization_bearer(self.owner_token)
        super(ResourceGenericTest, self).destroy(status_code=status.HTTP_403_FORBIDDEN, url=url)

    def owner_is_request_user(self):
        self.set_authorization_bearer(self.second_owner_token)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Resource.objects.get(id=owner_id)
        user = User.objects.get(username=self.second_owner_token)
        self.test_case.assertEqual(user, owner_obj.creator)

    def serializer_hyperlinked_fields(self, fields):
        fields.extend(['creator', 'account'])
        super(ResourceGenericTest, self).serializer_hyperlinked_fields(fields)

    def user_and_account_coincide_with_request_user(self):
        data = self.first_object_response.data
        account_id = data['account'].split('/')[-2]
        creator_id = data['creator'].split('/')[-2]
        request_user = User.objects.get(username=self.owner_token)
        self.test_case.assertEqual(account_id, str(request_user.accountuser.account.id))
        self.test_case.assertEqual(creator_id, str(request_user.id))

    def serializer_read_only_fields(self, fields):
        fields.extend(['creator', 'account'])
        super(ResourceGenericTest, self).serializer_read_only_fields(fields)
