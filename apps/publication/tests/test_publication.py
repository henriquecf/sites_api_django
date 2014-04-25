# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.utils import timezone
from rest_framework.test import APILiveServerTestCase

from apps.publication.tests import routines as publication_routines
from apps.resource.tests import routines as resource_routines
from apps.resource.models import AuthUser, User
import test_routines
import test_fixtures
from apps.publication.models import Publication, CustomHTML, find_available_slug


class PublicationTestCase(LiveServerTestCase):

    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(user=user, author=user, owner=user)
        publication = Publication.objects.create(owner=user, author=user, title='Test pub', content='Content')
        self.publication = publication

    def test_model_is_published_method(self):
        pub = self.publication
        self.assertTrue(pub.is_published())
        self.assertFalse(pub.unpublish())
        self.assertFalse(pub.is_published())
        self.assertTrue(pub.publish())
        self.assertTrue(pub.is_published())

    def test_model_publish_method(self):
        pub = self.publication
        tomorrow = timezone.now() + timezone.timedelta(1)
        pub.publication_start_date = tomorrow
        pub.save()
        self.assertFalse(pub.is_published())
        self.assertTrue(pub.publish())

    def test_model_unpublish_method(self):
        pub = self.publication
        self.assertFalse(pub.unpublish())
        self.assertTrue(pub.publish())
        pub.publication_end_date = timezone.now()
        pub.save()
        self.assertFalse(pub.is_published())
        self.assertTrue(pub.publish())

    def test_model_save_method(self):
        pub = self.publication
        pub.publication_start_date = timezone.datetime.now()
        pub.publication_end_date = timezone.datetime.now()
        self.assertFalse(timezone.is_aware(pub.publication_start_date))
        self.assertFalse(timezone.is_aware(pub.publication_end_date))
        pub.save()
        self.assertTrue(timezone.is_aware(pub.publication_start_date))
        self.assertTrue(timezone.is_aware(pub.publication_end_date))

    def test_find_available_slug_method(self):
        slug = 'test'
        pub = self.publication
        find_available_slug(Publication, pub, slug, slug)
        self.assertEqual(slug, pub.slug)
        pub.save()
        find_available_slug(Publication, pub, slug, slug)
        self.assertEqual(slug + '-2', pub.slug)
        pub.save()
        find_available_slug(Publication, pub, slug, slug)
        self.assertEqual(slug, pub.slug)


class PublicationAPITestCase(APILiveServerTestCase):
    model = Publication

    def setUp(self):
        self.url = reverse('publication-list')
        self.data = {
            'title': 'First publication'
        }
        self.altered_data = {
            'title': 'First publication altered'
        }
        test_fixtures.user_accountuser_account_permissions_token_fixture(self)
        self.set_authorization_bearer()
        self.first_object_response = self.client.post(self.url, self.data)

    def set_authorization_bearer(self, token=None):
        if not token:
            token = self.owner_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, response.data)
        self.assertEqual(0, response.data['count'])


class CustomHTMLAPITestCase(APILiveServerTestCase):
    model = CustomHTML

    def setUp(self):
        self.url = reverse('customhtml-list')
        self.data = {
            'title': 'First custom HTML',
            'content': 'HTML content',
        }
        self.altered_data = {
            'title': 'First custom HTML altered',
            'content': 'HTML content',
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