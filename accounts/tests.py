import copy
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from accounts.models import Common


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


class AccountTestCase(LiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create(username='user', password='123', email='user@user.com')

    def test_if_user_create_url_exists(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

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
        self.assertEqual(users_count + 1, new_users_count, 'User was not created')
        data.update({'username': 'ivan', 'email': ''})
        self.client.post(url, data)
        second_users_count = User.objects.count()
        self.assertEqual(new_users_count, second_users_count, 'User without email should not be created')

    def test_if_user_can_login(self):
        login_url = reverse('login')
        login_data = {
            'username': self.user.username,
            'password': self.user.password,
        }
        response = self.client.post(login_url, login_data)
        print(response.context)
        self.assertTrue(response.context['request'].user.is_authenticated())


# TODO Create tests to create app user, test if just owner and children access data