# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.sites.models import Site as ContribSite
from django.core.urlresolvers import reverse
from rest_framework import status

from apps.resource.models import Resource, Site
from test_routines import (
    test_serializer_hyperlinked_fields_routine,
    test_serializer_read_only_fields_routine,
)


def test_resource_owner_is_request_user_routine(test_case):
    test_case.set_authorization_bearer(test_case.second_owner_token)
    response = test_case.client.post(test_case.url, test_case.data)
    owner_id = response.data['url'].split('/')[-2]
    owner_obj = Resource.objects.get(id=owner_id)
    user = User.objects.get(username=test_case.second_owner_token)
    test_case.assertEqual(user, owner_obj.author)


def test_resource_serializer_hyperlinked_fields_routine(test_case, fields):
    test_serializer_hyperlinked_fields_routine(test_case, fields)


def test_resource_user_and_account_coincide_with_request_user_routine(test_case):
    data = test_case.first_object_response.data
    account_id = data['owner']['id']
    creator_id = data['author']['id']
    request_user = User.objects.get(username=test_case.owner_token)
    test_case.assertEqual(account_id, request_user.user.owner.id)
    test_case.assertEqual(creator_id, request_user.id)


def test_resource_serializer_read_only_fields_routine(test_case, fields):
    test_serializer_read_only_fields_routine(test_case, fields)


def test_resource_sites_field_routine(test_case):
    main_site, created = ContribSite.objects.get_or_create(domain='testserver')
    Site.objects.get_or_create(site=main_site, owner=test_case.owner, author=test_case.owner)
    test_case.data.update({'sites': [main_site.id]})
    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertIn('sites', response.data, 'Model has no field sites')
    test_case.assertIn(main_site.id, response.data['sites'])
    response2 = test_case.client.get(test_case.url)
    test_case.assertEqual(2, response2.data['count'], 'Looks like there is no filter for domain')
    my_site = ContribSite.objects.create(domain='otherserver.com')
    Site.objects.create(site=my_site, owner=test_case.owner, author=test_case.owner)
    test_case.data.update({'sites': [my_site.id]})
    response3 = test_case.client.put(response.data['url'], test_case.data)
    test_case.assertIn(my_site.id, response3.data['sites'])
    response4 = test_case.client.get(test_case.url)
    test_case.assertEqual(1, response4.data['count'], 'Looks like filter is not working properly')

    test_case.set_authorization_bearer(test_case.second_owner_token)
    test_case.data.update({'email': 'sites@sites.com'})
    response6 = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(status.HTTP_400_BAD_REQUEST, response6.status_code, response6.data)