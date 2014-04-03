from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from publication.tests import PublicationGenericTest, PublicationAPITestFunctions, PublicationAPITestFixtures
from .models import File


class FileAPITestFixtures(APILiveServerTestCase):
    model = File

    def setUp(self):
        self.url = reverse('file-list')
        self.data = {
            'title': 'First publication',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
        }
        self.altered_data = {
            'title': 'First publication altered',
            'description': 'First description altered',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
        }
        self.publication_generic_test = PublicationGenericTest(self)


class FileAPITestFunctions(PublicationAPITestFunctions):

    def test_add_category(self):
        self.publication_generic_test.add_category('file')


class FileAPITestCase(FileAPITestFixtures, FileAPITestFunctions):
    pass