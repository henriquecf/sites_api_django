# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import status
from resource.models import Resource
from test_routines import test_serializer_hyperlinked_fields_routine, test_serializer_read_only_fields_routine

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