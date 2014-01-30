import copy, time
from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
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
        self.client.force_authenticate(user=self.superuser)
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
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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