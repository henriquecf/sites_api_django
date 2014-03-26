import copy
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from rest_framework import status
from accounts.models import Common

from resource.models import Resource
from user.tests import APIGenericTest


class ResourceGenericTest(APIGenericTest):
    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(ResourceGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization_bearer(self.second_owner_token)
        super(ResourceGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False, url=url)

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
class UserTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='123', email='user@user.com')

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
            'username': 'user',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)

    def test_user_has_parent(self):
        children = User.objects.create_user(username='children', password='123', email='chidren@gmail.com')
        children.parent = self.user
        self.assertEqual(children.parent, self.user, 'User has no field parent')

    def test_database_exists(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.username, 'henrique')


class PermissionGenericTestCase:
    def __init__(self, test_case):
        self.test_case = test_case

    def model_has_custom_permission(self):
        model_name = self.test_case.model._meta.model_name
        view_permission = 'view_{0}'.format(model_name)
        database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename',
                                                                                                    flat=True)
        self.test_case.assertIn(view_permission, database_permissions)


class ResourcePermissionTestCase(LiveServerTestCase):
    model = Resource

    def setUp(self):
        self.permission_test_case = PermissionGenericTestCase(self)

    def test_model_has_custom_permission(self):
        self.permission_test_case.model_has_custom_permission()