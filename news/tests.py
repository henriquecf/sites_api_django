from django.core.urlresolvers import reverse, NoReverseMatch
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from publication.test_publication import PublicationAPITestCase


class NewsAPITestCase(PublicationAPITestCase):
    url = reverse('news-list')
