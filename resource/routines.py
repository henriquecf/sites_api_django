# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from rest_framework import status
from resource.models import Resource, AccountSite
from test_routines import (
    test_serializer_hyperlinked_fields_routine,
    test_serializer_read_only_fields_routine,
    test_resource_permission_routine,
)


def test_resource_owner_is_request_user_routine(test_case):
    test_case.set_authorization_bearer(test_case.second_owner_token)
    response = test_case.client.post(test_case.url, test_case.data)
    owner_id = response.data['url'].split('/')[-2]
    owner_obj = Resource.objects.get(id=owner_id)
    user = User.objects.get(username=test_case.second_owner_token)
    test_case.assertEqual(user, owner_obj.creator)


def test_resource_serializer_hyperlinked_fields_routine(test_case, fields):
    fields.extend(['creator', 'account'])
    test_serializer_hyperlinked_fields_routine(test_case, fields)


def test_resource_user_and_account_coincide_with_request_user_routine(test_case):
    data = test_case.first_object_response.data
    account_id = data['account'].split('/')[-2]
    creator_id = data['creator'].split('/')[-2]
    request_user = User.objects.get(username=test_case.owner_token)
    test_case.assertEqual(account_id, str(request_user.accountuser.account.id))
    test_case.assertEqual(creator_id, str(request_user.id))


def test_resource_serializer_read_only_fields_routine(test_case, fields):
    fields.extend(['creator', 'account'])
    test_serializer_read_only_fields_routine(test_case, fields)


def test_resource_sites_field_routine(test_case):
    main_site, created = Site.objects.get_or_create(domain='testserver')
    accountsite = AccountSite.objects.get(site=main_site, account=test_case.owner.account)
    site_url = reverse('accountsite-detail', args=(accountsite.id,))
    response0 = test_case.client.get(site_url)
    test_case.assertIn('url', response0.data, response0.data)
    site_obj_url = response0.data['url']
    test_case.data.update({'sites': [site_obj_url]})
    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertIn('sites', response.data, 'Model has no field sites')
    test_case.assertIn(site_obj_url, response.data['sites'])
    response2 = test_case.client.get(test_case.url)
    test_case.assertEqual(2, response2.data['count'], 'Looks like there is no filter for domain')
    my_site = Site.objects.create(domain='otherserver.com')
    my_accountsite = AccountSite.objects.create(site=my_site, account=test_case.owner.account)
    site_url2 = reverse('accountsite-detail', args=(my_accountsite.id,))
    my_site_url = test_case.client.get(site_url2).data['url']
    test_case.data.update({'sites': [my_site_url]})
    response3 = test_case.client.put(response.data['url'], test_case.data)
    test_case.assertIn(my_site_url, response3.data['sites'])
    response4 = test_case.client.get(test_case.url)
    test_case.assertEqual(1, response4.data['count'], 'Looks like filter is not working properly')

    test_case.set_authorization_bearer(test_case.second_owner_token)
    response5 = test_case.client.get(site_url)
    test_case.assertEqual(status.HTTP_404_NOT_FOUND, response5.status_code, response5.data)

    response6 = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(status.HTTP_400_BAD_REQUEST, response6.status_code, response6.data)