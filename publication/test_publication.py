import copy
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from oauth2_provider.models import Application, AccessToken
from publication.models import Common


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


#TODO Refactor publication test cases, at least removing duplicated code
class PublicationAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.url = reverse('publication-list')
        self.data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        self.superuser = User.objects.create_superuser(username='superuser', email='su@su.com', password='123')
        aplicacao = Application.objects.create(user=self.superuser, client_type='confidential', authorization_grant_type='password', client_id='12345')
        access_token = AccessToken.objects.create(user=self.superuser, token='12345', application=aplicacao, expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
        super(PublicationAPITestCase, self).setUp()


    def test_create_publication(self):
        """
        Ensure we can create a new publication object
        """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_blank_publication(self):
        """
        Ensure it does not accept the data when some mandatory fields are sent without data
        """
        self.data = {
            'title': None,
            'description': None,
            'slug': None,
            'publication_start_date': None,
            'publication_end_date': None,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_is_generated_automatically(self):
        """
        Checks if the slug is generated automatically
        """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['slug'], slugify(self.data['title']))

    def test_slug_is_unique(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['slug'], slugify(self.data['title']))
        response2 = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['slug'], slugify(self.data['title'] + "-2"))
        response3 = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response3.data['slug'], slugify(self.data['title'] + "-3"))

    def test_do_not_create_publication_without_authentication(self):
        """
        Ensure we can create a new publication object
        """
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publication_has_author(self):
        """
        Ensure publication created has author
        """
        response = self.client.post(self.url, self.data, format='json')
        self.assertIn('author', list(response.data))
        self.assertEqual(response.data['author'], self.superuser.username)

    def test_list_publication(self):
        """
        Posts some publication and retrieves them back, even when not authenticated
        """
        self.client.post(self.url, self.data, formart='json')
        self.client.post(self.url, self.data, formart='json')
        self.client.post(self.url, self.data, formart='json')
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 3)

    def test_retrive_url_from_list(self):
        """
        Gets a publication list and retrieves the field url from each publication in the list
        """
        self.client.post(self.url, self.data, formart='json')
        self.client.post(self.url, self.data, formart='json')
        self.client.post(self.url, self.data, formart='json')
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertIn('url', list(response.data['results'][0]))
        detail_url = response.data['results'][0]['url']
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_updates_publication(self):
        """
        Tests if an authenticated user can update a publication
        """
        response = self.client.post(self.url, self.data, format='json')
        unaltered_data = copy.copy(response.data)
        altered_data = response.data
        altered_data['title'] = 'Altered title'
        response2 = self.client.patch(altered_data['url'], altered_data)
        self.assertNotEqual(unaltered_data['title'], response2.data['title'])

    def test_unauthenticated_user_can_not_update_publication(self):
        response = self.client.post(self.url, self.data, format='json')
        self.client.credentials()
        altered_data = response.data
        altered_data['title'] = 'Altered title'
        response2 = self.client.patch(altered_data['url'], altered_data)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_deletes_publication(self):
        response = self.client.post(self.url, self.data, format='json')
        detail_url = response.data['url']
        response2 = self.client.delete(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_user_can_not_delete_publication(self):
        response = self.client.post(self.url, self.data, format='json')
        self.client.credentials()
        detail_url = response.data['url']
        response2 = self.client.delete(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_publication_is_published_or_not(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertIn('is_published', list(response.data))
        is_published_url = response.data['is_published']
        response2 = self.client.get(is_published_url)
        self.assertTrue(response2.data)
        altered_data = copy.copy(response.data)
        altered_data['publication_end_date'] = datetime.now()
        response3 = self.client.patch(response.data['url'], altered_data)
        response4 = self.client.get(response3.data['is_published'])
        self.assertFalse(response4.data)

    def test_if_publication_publishes(self):
        response = self.client.post(self.url, self.data, format='json')
        altered_data = copy.copy(response.data)
        altered_data['publication_end_date'] = datetime.now()
        response2 = self.client.patch(response.data['url'], altered_data)
        response3 = self.client.get(response2.data['is_published'])
        self.assertFalse(response3.data)
        self.assertIn('publish', list(response.data))
        publish_url = response.data['publish']
        response4 = self.client.get(publish_url)
        self.assertTrue(response4.data)

    def test_if_publication_unpublishes(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertIn('is_published', list(response.data))
        is_published_url = response.data['is_published']
        response2 = self.client.get(is_published_url)
        self.assertTrue(response2.data)
        self.assertIn('unpublish', response.data)
        unpublish_url = response.data['unpublish']
        response3 = self.client.get(unpublish_url)
        self.assertFalse(response3.data)

    def test_if_non_owner_cannot_access_others_data(self):
        response = self.client.post(self.url, self.data)
        pub_url = response.data['url']
        other_user = User.objects.create(username='henrique', password='123', email='h@g.com')
        aplicacao = Application.objects.create(user=other_user, client_type='confidential', authorization_grant_type='password', client_id='123456')
        access_token = AccessToken.objects.create(user=other_user, token='123456', application=aplicacao, expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
        response2 = self.client.get(pub_url)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_list_retrieves_just_owner_data(self):
        self.client.post(self.url, self.data)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
        other_user = User.objects.create(username='henrique', password='123', email='h@g.com')
        aplicacao = Application.objects.create(user=other_user, client_type='confidential', authorization_grant_type='password', client_id='123456')
        access_token = AccessToken.objects.create(user=other_user, token='123456', application=aplicacao, expires=datetime.now() + timedelta(0, 60))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token.token)
        response2 = self.client.get(self.url)
        self.assertEqual(response2.data['count'], 0)