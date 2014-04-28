# -*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django.http.request import HttpRequest

from apps.resource.serializers import ResourceSerializer
from apps.resource.models import Site, Resource, ContribSite, AuthUser, User
from apps.resource.views import ResourceViewSet
from test_fixtures import user_accountuser_account_permissions_token_fixture


class ResourceTestCase(TestCase):
    model = Resource

    def test_sites_filter_get_fields_serializer(self):
        user_accountuser_account_permissions_token_fixture(self)
        request = HttpRequest()
        request.user = self.owner
        site = ContribSite.objects.first()
        Site.objects.create(owner=self.owner, site=site, author=self.owner)
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertIn(site, possible_sites)

        other_site = ContribSite.objects.create()
        Site.objects.create(owner=self.second_owner, site=other_site,
                            author=self.second_owner)
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertIn(site, possible_sites)
        self.assertNotIn(other_site, possible_sites)

        request.user = self.second_owner
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertNotIn(site, possible_sites)
        self.assertIn(other_site, possible_sites)

    def test_pre_save_post_save_methods(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(owner=user, author=user, user=user)
        request = HttpRequest()
        request.user = user
        viewset = ResourceViewSet(request=request)
        resource = Resource()
        viewset.pre_save(resource)
        self.assertEqual(user, resource.owner)
        self.assertEqual(user, resource.author)

        resource.save()
        request.META['HTTP_HOST'] = 'testserver'

        viewset.post_save(resource)
        site = ContribSite.objects.get(domain='testserver')
        self.assertIn(site, resource.sites.all())
