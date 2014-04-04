from django.utils import timezone
from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.test import PublicationGenericTest, PublicationAPITestFunctions
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

    def test_filter_by_category_name(self):
        category_url = reverse('category-list')
        category_data = {
            'name': 'Category 1',
            'model_name': 'news',
        }
        category_response = self.client.post(category_url, category_data)
        response_news = self.client.post(self.url, self.data)
        response_news2 = self.client.patch(response_news.data['url'], {'categories': [category_response.data['url']]})
        self.assertEqual(response_news2.status_code, status.HTTP_200_OK, response_news2.data)
        filter = {
            'categories': 'Category 1',
        }
        response = self.client.get(self.url, filter)
        self.assertEqual(response.data['count'], 1)
        category_data2 = {
            'name': 'Category 2',
            'model_name': 'news',
        }
        category_response2 = self.client.post(category_url, category_data2)
        self.client.patch(response_news.data['url'],
                          {'categories': [category_response.data['url'], category_response2.data['url']]})
        filter2 = {
            'categories': ['Category 1', 'Category 2']
        }
        response2 = self.client.get(self.url, filter2)
        self.assertEqual(response2.data['count'], 1)

