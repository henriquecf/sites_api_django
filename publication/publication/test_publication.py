import copy, time
from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.models import Common

# TODO Create common class that will store creation date, last modification date,
#  author and last editor and will be inhereted by all the others
class CommonTestCase(LiveServerTestCase):

    def test_create_common_fields(self):
        """
        Ensure common is created
        """
        common = Common.objects.create()
        self.assertTrue(common.creation_date)
        self.assertTrue(common.last_modification_date)

    def test_update_common_fields(self):
        """
        Ensure common field last_modification_date is changed when object is saved
        """
        common = Common.objects.create()
        common2 = copy.copy(common)
        common.save()
        self.assertNotEqual(common.last_modification_date, common2.last_modification_date)


class CreatePublicationAPITestCase(APILiveServerTestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(username='superuser', email='su@su.com', password='123')
        self.client.force_authenticate(user=self.superuser)
        super(CreatePublicationAPITestCase, self).setUp()


    def test_create_publication(self):
        """
        Ensure we can create a new publication object
        """
        url = reverse('publication-list')
        data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_blank_publication(self):
        """
        Ensure it does not accept the data when some mandatory fields are sent without data
        """
        url = reverse('publication-list')
        data = {
            'title': None,
            'description': None,
            'slug': None,
            'publication_start_date': None,
            'publication_end_date': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_is_generated_automatically(self):
        """
        Checks if the slug is generated automatically
        """
        url = reverse('publication-list')
        data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'other-slug',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['slug'], slugify(data['title']))

    def test_slug_is_unique(self):
        url = reverse('publication-list')
        data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'other-slug',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['slug'], slugify(data['title']))
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['slug'], slugify(data['title'] + "-2"))

    def test_do_not_create_publication_without_authentication(self):
        """
        Ensure we can create a new publication object
        """
        url = reverse('publication-list')
        data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publication_has_author(self):
        """
        Ensure publication created has author
        """
        url = reverse('publication-list')
        data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': datetime(2014, 1, 29, 19, 10, 7),
            'publication_end_date': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertIn('author', list(response.data))
        self.assertEqual(response.data['author'], self.superuser.username)