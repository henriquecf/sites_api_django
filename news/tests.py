from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase

from publication.tests import PublicationGenericTest, PublicationAPITestFixtures, PublicationAPITestFunctions
from .models import News


class NewsAPITestFixtures(APILiveServerTestCase):
    model = News

    def setUp(self):
        self.url = reverse('news-list')
        self.data = {
            'title': 'First news',
            'description': 'First description',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
            'content': 'My first news',
        }
        self.altered_data = {
            'title': 'First news altered',
            'description': 'First description altered',
            'slug': 'first-publication',
            'publication_start_date': timezone.now(),
            'publication_end_date': None,
            'content': 'My first news altered',
        }
        self.publication_generic_test = PublicationGenericTest(self)

class NewsAPITestFunctions(PublicationAPITestFunctions):
    search_fields = ('title', 'description', 'content')

    def test_add_category(self):
        self.publication_generic_test.add_category('news')

class NewsAPITestCase(NewsAPITestFixtures, NewsAPITestFunctions):
    pass