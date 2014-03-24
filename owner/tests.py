import copy
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from rest_framework import status

from owner.models import Owner, Common
from user.tests import APIGenericTest


class OwnerAndChildrenGenericTest(APIGenericTest):
    def __init__(self, test_case, initial_user_is_superuser=False):
        super(OwnerAndChildrenGenericTest, self).__init__(test_case,
                                                          initial_user_is_superuser=initial_user_is_superuser)
        self.children_user = User.objects.create_user(username='children', password='123', email='children@gm.com',
                                                      parent=self.user)

    def create(self, status_code=status.HTTP_201_CREATED):
        super(OwnerAndChildrenGenericTest, self).create(status_code=status_code)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).create(status_code=status_code)
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).create(status_code=status.HTTP_401_UNAUTHORIZED)
        self.reset_authorization()

    def update(self, status_code=status.HTTP_200_OK, is_altered=True):
        super(OwnerAndChildrenGenericTest, self).update(status_code=status_code)
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).update(status_code=status.HTTP_401_UNAUTHORIZED, is_altered=False)
        self.set_authorization(random_user=True)
        super(OwnerAndChildrenGenericTest, self).update(status_code=status.HTTP_201_CREATED)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).update(status_code=status.HTTP_201_CREATED)
        self.reset_authorization()

    def partial_update(self, status_code=status.HTTP_200_OK, is_altered=True):
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status_code)
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status.HTTP_401_UNAUTHORIZED,
                                                                is_altered=False)
        self.set_authorization(random_user=True)
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).partial_update(status_code=status.HTTP_404_NOT_FOUND, is_altered=False)
        self.reset_authorization()

    def list(self, count=1, status_code=status.HTTP_200_OK):
        super(OwnerAndChildrenGenericTest, self).list(count=count, status_code=status_code)
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).list(count=-1, status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerAndChildrenGenericTest, self).list(count=0, status_code=status_code)
        self.set_authorization(user=self.children_user)
        self.test_case.client.post(self.url, self.data)
        super(OwnerAndChildrenGenericTest, self).list(count=1, status_code=status_code)
        self.reset_authorization()
        super(OwnerAndChildrenGenericTest, self).list(count=count+1, status_code=status_code)
        self.reset_authorization()

    def retrieve(self, status_code=status.HTTP_200_OK):
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status_code)
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).retrieve(status_code=status.HTTP_404_NOT_FOUND)
        self.reset_authorization()

    def destroy(self, status_code=status.HTTP_204_NO_CONTENT):
        self.test_case.client.credentials()
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status.HTTP_401_UNAUTHORIZED)
        self.set_authorization(random_user=True)
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.set_authorization(user=self.children_user)
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status.HTTP_404_NOT_FOUND)
        self.reset_authorization()
        super(OwnerAndChildrenGenericTest, self).destroy(status_code=status_code)

    def owner_or_children_is_request_user(self):
        username = self.set_authorization(random_user=True)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Owner.objects.get(id=owner_id)
        user = User.objects.get(username=username)
        self.test_case.assertEqual(user, owner_obj.owner)
        username = self.set_authorization(user=self.children_user)
        response = self.test_case.client.post(self.url, self.data)
        owner_id = response.data['url'].split('/')[-2]
        owner_obj = Owner.objects.get(id=owner_id)
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