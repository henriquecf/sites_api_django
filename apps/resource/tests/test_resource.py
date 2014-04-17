# -*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django.http.request import HttpRequest
from apps.resource.serializers import ResourceSerializer
from apps.resource.models import AccountSite, Site, Resource
from test_fixtures import user_accountuser_account_permissions_token_fixture


class ResourceTestCase(TestCase):
    model = Resource

    def setUp(self):
        user_accountuser_account_permissions_token_fixture(self)

    def test_sites_filter_get_fields_serializer(self):
        request = HttpRequest()
        request.user = self.owner
        site = Site.objects.first()
        accountsite = AccountSite.objects.create(account=self.owner.account, site=site)
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertIn(site, possible_sites)

        other_site = Site.objects.create()
        other_user_accountsite = AccountSite.objects.create(account=self.second_owner.account,
                                                            site=other_site)
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertIn(site, possible_sites)
        self.assertNotIn(other_site, possible_sites)

        request.user = self.second_owner
        possible_sites = ResourceSerializer(context={'request': request}).get_fields()['sites'].queryset
        self.assertNotIn(site, possible_sites)
        self.assertIn(other_site, possible_sites)