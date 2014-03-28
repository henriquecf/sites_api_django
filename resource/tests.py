from django.contrib.auth.models import User, Permission
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

    def __init__(self, test_case):
        self.test_case = test_case
        self.url = self.test_case.url
        self.data = self.test_case.data
        self.altered_data = self.test_case.altered_data
        self.owner_token = AccessToken.objects.get(id=1).token
        self.account_user_token = AccessToken.objects.get(id=2).token
        self.account_user_token2 = AccessToken.objects.get(id=3).token
        self.account_user_token3 = AccessToken.objects.get(id=4).token
        self.second_owner_token = AccessToken.objects.get(id=5).token
        self.second_account_user_token = AccessToken.objects.get(id=6).token
        self.second_account_user_token2 = AccessToken.objects.get(id=7).token
        self.second_account_user_token3 = AccessToken.objects.get(id=8).token
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
        self.create(status_code=status.HTTP_403_FORBIDDEN)
        self.update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False)
        self.partial_update(status_code=status.HTTP_403_FORBIDDEN, is_altered=False)
        self.list(count=-1, status_code=status.HTTP_403_FORBIDDEN)
        self.retrieve(status_code=status.HTTP_403_FORBIDDEN)
        self.destroy(status_code=status.HTTP_403_FORBIDDEN)

    def search_fields(self, search_fields=None):
        for field in search_fields:
            filter_parameter = random.randint(1, 999999)
            self.altered_data.update({field: filter_parameter})
            self.test_case.client.post(self.url, self.altered_data)
            query_parameter = {'search': filter_parameter}
            response = self.test_case.client.get(self.url, query_parameter)
            self.test_case.assertEqual(response.data['count'], 1, 'Field "{0}" not in search fields'.format(field))

            # TODO Still need to create a generic test for ordering

    def hyperlinked_fields(self, fields):
        for field in fields:
            response = self.test_case.client.get(self.first_object_response.data[field])
            self.test_case.assertEqual(response.status_code, status.HTTP_200_OK, 'Error with field {0}'.format(field))


class PermissionGenericTest(APIGenericTest):

    def model_has_custom_permission(self):
        model_name = self.test_case.model._meta.model_name
        view_permission = 'view_{0}'.format(model_name)
        database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename',
                                                                                                    flat=True)
        self.test_case.assertIn(view_permission, database_permissions)


class ResourceGenericTest(PermissionGenericTest):

    def create(self, status_code=status.HTTP_201_CREATED):
        super(ResourceGenericTest, self).create(status_code=status_code)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).create(status_code=status_code)

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

    def hyperlinked_fields(self, fields):
        if not fields:
            fields = ['creator', 'account']
        else:
            fields.append('creator')
            fields.append('account')
        super(ResourceGenericTest, self).hyperlinked_fields(fields)

    def user_and_account_from_request_user(self):
        data = self.first_object_response.data
        account_id = data['account'].split('/')[-2]
        creator_id = data['creator'].split('/')[-2]
        request_user = User.objects.get(username=self.owner_token)
        self.test_case.assertEqual(account_id, str(request_user.accountuser.account.id))
        self.test_case.assertEqual(creator_id, str(request_user.id))