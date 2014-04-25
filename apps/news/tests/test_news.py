# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http.request import HttpRequest
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase

from apps.category.tests.routines import test_add_category_routine, test_filter_categories
from apps.category.models import Category
from apps.publication.tests import routines as publication_routines
from apps.publication.models import Publication
from apps.resource.tests import routines as resource_routines
from apps.resource.models import AuthUser, User
import test_routines
import test_fixtures
from apps.news.models import News
from apps.news.serializers import NewsSerializer


class FileTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        self.news = News.objects.create(owner=user, author=user, title='Page')
        self.user = user
        self.request = HttpRequest()
        self.request.user = user

    def test_serializer_get_fields_method(self):
        news_content_type = ContentType.objects.get_for_model(News)
        category = Category.objects.create(owner=self.user, author=self.user, name='Category', model=news_content_type)
        news_serializer = NewsSerializer(context={'request': self.request})
        categories = news_serializer.get_fields()['categories'].queryset.all()
        self.assertIn(category, categories)
        category.model = ContentType.objects.get_for_model(User)
        category.save()
        categories = news_serializer.get_fields()['categories'].queryset.all()
        self.assertNotIn(category, categories)
        category.model = news_content_type
        other_user = AuthUser.objects.create_user(username='other_user', password='123')
        User.objects.create(owner=other_user, user=other_user, author=other_user)
        category.owner = other_user
        category.save()
        categories = news_serializer.get_fields()['categories'].queryset.all()
        self.assertNotIn(category, categories)


class NewsAPITestCase(APILiveServerTestCase):
    model = News

    def setUp(self):
        self.url = reverse('news-list')
        self.data = {
            'title': 'First news',
            'content': 'Content',
        }
        self.altered_data = {
            'title': 'First news altered',
            'content': 'Content altered',
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_slug_is_slugified_title(self):
        publication_routines.test_slug_is_slugified_title_routine(self)

    def test_slug_is_unique(self):
        publication_routines.test_slug_is_unique_routine(self)

    def test_has_author(self):
        publication_routines.test_has_author_routine(self)

    def test_is_published_default_true(self):
        publication_routines.test_is_published_default_true_routine(self)

    def test_publish(self):
        publication_routines.test_publish_routine(self)

    def test_unpublish(self):
        publication_routines.test_unpublish_routine(self)

    def test_search_fields(self):
        fields = ['title', 'description', 'content']
        test_routines.test_search_fields_routine(self, search_fields=fields)

    def test_resource_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_publication_serializer_hyperlinked_fields(self):
        publication_routines.test_publication_serializer_hyperlinked_fields_routine(self, fields=[])

    def test_resource_user_and_account_coincide_with_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_resource_serializer_read_only_fields(self):
        resource_routines.test_resource_serializer_read_only_fields_routine(self, fields=[])

    def test_add_category(self):
        test_add_category_routine(self)

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_categories_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        news_content_type = ContentType.objects.get_for_model(News)
        category = Category.objects.create(author=self.owner, owner=self.owner, name='Category 1',
                                           model=news_content_type)
        possible_categories = NewsSerializer(context={'request': request}).get_fields()['categories'].queryset
        self.assertIn(category, possible_categories)
        other_user_category = Category.objects.create(author=self.second_owner, owner=self.second_owner,
                                                      name='Other category', model=news_content_type)

        possible_categories = NewsSerializer(context={'request': request}).get_fields()['categories'].queryset
        self.assertIn(category, possible_categories)
        self.assertNotIn(other_user_category, possible_categories)

        request.user = self.second_owner

        possible_categories = NewsSerializer(context={'request': request}).get_fields()['categories'].queryset
        self.assertNotIn(category, possible_categories)
        self.assertIn(other_user_category, possible_categories)

        publication_content_type = ContentType.objects.get_for_model(Publication)

        other_user_category.model = publication_content_type
        other_user_category.save()

        possible_categories = NewsSerializer(context={'request': request}).get_fields()['categories'].queryset
        self.assertNotIn(category, possible_categories)
        self.assertNotIn(other_user_category, possible_categories)

        category.model = publication_content_type
        category.save()
        request.user = self.owner

        possible_categories = NewsSerializer(context={'request': request}).get_fields()['categories'].queryset
        self.assertNotIn(category, possible_categories)
        self.assertNotIn(other_user_category, possible_categories)


# TODO Functional: filter categories field filterset