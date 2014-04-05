# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class UserTestCase(LiveServerTestCase):

    def setUp(self):
        User.objects.create_user('henrique', 'elo.henrique@gmail.com', '123')

    def test_user_login(self):
        login_url = reverse('login')
        login_data = {
            'username': 'henrique',
            'password': '123',
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)