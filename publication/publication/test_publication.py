from datetime import datetime
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

# TODO Test if just authenticated user can create a publication
# TODO Generate slug automatically
# TODO Create common class that will store creation date, last modification date,
#  author and last editor and will be inhereted by all the others
class CreatePublicationAPITestCase(APILiveServerTestCase):

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
        self.assertEqual(response.data, data)