# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.test import LiveServerTestCase
from rest_framework.test import APILiveServerTestCase
from rest_framework import status
from apps.resource.tests import routines as resource_routines
from apps.resource.models import AuthUser, User
from apps.publication.tests import routines as publication_routines
import test_routines
import test_fixtures
from apps.cms.models import Page


class PageTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        self.page = Page.objects.create(owner=user, author=user, title='Page')
        self.user = user

    def test_save_method(self):
        self.assertTrue(self.page.category)
        self.assertEqual(self.page.category.name, self.page.slug)
        self.assertEqual(self.page.category.model, ContentType.objects.get_for_model(Page))
        self.assertEqual(self.page.category.owner, self.page.owner)
        self.assertEqual(self.page.category.author, self.page.author)


class PageAPITestCase(APILiveServerTestCase):
    model = Page

    def setUp(self):
        self.url = reverse('page-list')
        self.data = {
            'title': 'First Page',
        }
        self.altered_data = {
            'title': 'First Page Altered',
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_api_basic_methods(self):
        test_routines.test_api_basic_methods_routine(self)

    def test_resource_permission(self):
        test_routines.test_resource_permission_routine(self)

    def test_admin_permission(self):
        test_routines.test_admin_permission_routine(self)

    def test_custom_object_permission(self):
        test_routines.test_custom_object_permission_routine(self)

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
        search_fields = ['title', 'description']
        test_routines.test_search_fields_routine(self, search_fields=search_fields)

    def test_owner_is_request_user(self):
        resource_routines.test_resource_owner_is_request_user_routine(self)

    def test_publication_serializer_hyperlinked_fields(self):
        publication_routines.test_publication_serializer_hyperlinked_fields_routine(self, [])

    def test_user_and_account_from_request_user(self):
        resource_routines.test_resource_user_and_account_coincide_with_request_user_routine(self)

    def test_model_has_custom_permission(self):
        test_routines.test_model_has_custom_permission_routine(self)

    def test_publication_serializer_read_only_fields(self):
        resource_routines.test_serializer_read_only_fields_routine(self, [])

    def test_resource_sites_field(self):
        resource_routines.test_resource_sites_field_routine(self)

    def test_create_category(self):
        self.assertIn('category', self.first_object_response.data)
        self.assertIsNotNone(self.first_object_response.data['category'])
        category_url = self.first_object_response.data['category']
        category_response = self.client.get(category_url)
        self.assertEqual(status.HTTP_200_OK, category_response.status_code)

    def test_modules_field(self):
        self.assertIn('modules', self.first_object_response.data)


# TODO Unit tests: save (page model), get_content_url (module serializer), get_fields (page serializer), post_save (page viewset)