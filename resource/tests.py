import copy
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from rest_framework import status

from resource.models import Resource, Common
from user.tests import APIGenericTest


class OwnerGenericTest(APIGenericTest):
    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(OwnerGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=is_altered, url=url)

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(OwnerGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False, url=url)

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(OwnerGenericTest, self).list(count=count, status_code=status_code)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).list(count=0, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(OwnerGenericTest, self).retrieve(status_code=status_code, url=url)
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND, url=url)

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        self.set_authorization(random_user=True)
        super(OwnerGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND, url=url)
        self.reset_authorization()
        super(OwnerGenericTest, self).destroy(status_code=status_code, url=url)

    def owner_is_request_user(self):
        username = self.set_authorization(random_user=True)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Resource.objects.get(id=owner_id)
        user = User.objects.get(username=username)
        self.test_case.assertEqual(user, owner_obj.owner)


class OwnerAndChildrenGenericTest(OwnerGenericTest):

    def __init__(self, test_case, initial_user_is_superuser=False):
        super(OwnerAndChildrenGenericTest, self).__init__(test_case,
                                                          initial_user_is_superuser=initial_user_is_superuser)
        self.children_user = User.objects.create_user(username='children', password='123', email='children@gm.com',
                                                      parent=self.user)

    def create(self, status_code=status.HTTP_201_CREATED):
        super(OwnerAndChildrenGenericTest, self).create(status_code=status_code)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).create(status_code=status_code)

    def update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(OwnerAndChildrenGenericTest, self).update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).update(status_code=status.HTTP_201_CREATED, is_altered=is_altered,
                                                        url=url)
        response = self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).update(status_code=status_code, is_altered=is_altered,
                                                        url=response.data['url'])

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True, url=None):
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered, url=url)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False,
                                                                url=url)
        response = self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status_code, is_altered=is_altered,
                                                                url=response.data['url'])

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(OwnerAndChildrenGenericTest, self).list(count=count, status_code=status_code)
        self.set_authorization(user=self.children_user)
        self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).list(count=1, status_code=status_code)
        self.reset_authorization()
        super(OwnerAndChildrenGenericTest, self).list(count=count + 1, status_code=status_code)

    def retrieve(self, status_code=status.HTTP_200_OK, url=None):
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status_code)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        response = self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status_code, url=response.data['url'])

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT, url=None):
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status_code, url=url)
        self.set_authorization(user=self.children_user)
        response = self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status_code, url=response.data['url'])

    def owner_or_children_is_request_user(self):
        super(OwnerAndChildrenGenericTest, self).owner_is_request_user()
        username = self.set_authorization(user=self.children_user)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Resource.objects.get(id=owner_id)
        user = User.objects.get(username=username)
        self.test_case.assertEqual(user, owner_obj.children)
        self.reset_authorization()


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

    def test_user_create_url_exists(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
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


class PermissionGenericTestCase:
    def __init__(self, test_case):
        self.test_case = test_case

    def model_has_custom_permission(self):
        model_name = self.test_case.model._meta.model_name
        permission_labels = ['read', 'add', 'change', 'delete']
        permissions = ['{0}_global_{1}'.format(permission_label, model_name) for permission_label in permission_labels]
        read_nonglobal_permission = 'read_{0}'.format(model_name)
        permissions.append(read_nonglobal_permission)
        database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename',
                                                                                                    flat=True)
        for permission in permissions:
            self.test_case.assertIn(permission, database_permissions)


class OwnerPermissionTestCase(LiveServerTestCase):
    model = Resource

    def setUp(self):
        self.permission_test_case = PermissionGenericTestCase(self)

    def test_model_has_custom_permission(self):
        self.permission_test_case.model_has_custom_permission()