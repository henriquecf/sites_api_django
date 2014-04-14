# -*- coding: utf-8 -*-
import random
from django.contrib.auth.models import Permission
from rest_framework import status


def test_api_basic_methods_routine(test_case, token=None, count=2, object_url=None):
    if not token:
        token = test_case.owner_token
    test_case.set_authorization_bearer(token)

    if not object_url:
        object_url = test_case.first_object_response.data['url']

    # Test POST
    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)

    # Test PUT
    response = test_case.client.put(object_url, test_case.altered_data)
    test_case.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    # Test PATCH
    response = test_case.client.patch(object_url, test_case.altered_data)
    test_case.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    # Test RETRIEVE
    response = test_case.client.get(object_url)
    test_case.assertEqual(status.HTTP_200_OK, response.status_code, response.data)

    # Test LIST
    response = test_case.client.get(test_case.url)
    test_case.assertEqual(status.HTTP_200_OK, response.status_code)
    test_case.assertEqual(count, response.data['count'])

    # Test DELETE
    response = test_case.client.delete(object_url)
    test_case.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.data)
    

def test_admin_permission_routine(test_case, token=None):
    if not token:
        token = test_case.account_user_token
    test_case.set_authorization_bearer(token)

    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    response2 = test_case.client.put(test_case.first_object_response.data['url'], test_case.altered_data)
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response2.status_code)

    response3 = test_case.client.patch(test_case.first_object_response.data['url'], test_case.altered_data)
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response3.status_code)

    response4 = test_case.client.get(test_case.first_object_response.data['url'])
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response4.status_code)

    response5 = test_case.client.get(test_case.url)
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response5.status_code)

    response6 = test_case.client.delete(test_case.first_object_response.data['url'])
    test_case.assertEqual(status.HTTP_403_FORBIDDEN, response6.status_code)


def test_serializer_hyperlinked_fields_routine(test_case, fields):
    fields.extend(['url'])
    for field in fields:
        response = test_case.client.get(test_case.first_object_response.data[field])
        test_case.assertEqual(response.status_code, status.HTTP_200_OK, 'Error with field {0}'.format(field))


def test_model_has_custom_permission_routine(test_case):
    model_name = test_case.model._meta.model_name
    view_permission = 'view_{0}'.format(model_name)
    database_permissions = Permission.objects.filter(codename__endswith=model_name).values_list('codename', flat=True)
    test_case.assertIn(view_permission, database_permissions)


def test_serializer_read_only_fields_routine(test_case, fields):
    for field in fields:
        response = test_case.client.options(test_case.url)
        test_case.assertEqual(True, response.data['actions']['POST'][field]['read_only'])


def test_search_fields_routine(test_case, search_fields):
    for field in search_fields:
        filter_parameter = random.randint(1, 999999)
        test_case.altered_data.update({field: filter_parameter})
        test_case.client.post(test_case.url, test_case.altered_data)
        query_parameter = {'search': filter_parameter}
        response = test_case.client.get(test_case.url, query_parameter)
        test_case.assertEqual(1, response.data['count'], 'Field "{0}" not in search fields'.format(field))


def test_custom_object_permission_routine(test_case, count=3):

    # Removes permission from the owner
    test_case.owner.user_permissions.clear()

    # Now he is not allowed to access anything
    test_admin_permission_routine(test_case, token=test_case.owner_token)

    # Changes to an user that has global permissions
    # He should get the same treatment as the owner
    test_api_basic_methods_routine(test_case, token=test_case.account_user_token2)

    # Now the global permissions are removed from the user that had them
    test_case.account_user2.creator_restrictions.clear()

    # He should get restrictions to owner resources now
    test_resource_permission_routine(test_case, token=test_case.account_user_token2, count=count)


def test_resource_permission_routine(test_case, token=None, count=2):
    if not token:
        token = test_case.second_owner_token
    test_case.set_authorization_bearer(token)

    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)

    response = test_case.client.put(test_case.first_object_response.data['url'], test_case.altered_data)
    test_case.assertEqual(status.HTTP_201_CREATED, response.status_code, response.data)

    response = test_case.client.patch(test_case.first_object_response.data['url'], test_case.altered_data)
    test_case.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    response = test_case.client.get(test_case.url)
    test_case.assertEqual(status.HTTP_200_OK, response.status_code)
    test_case.assertEqual(count, response.data['count'])

    response = test_case.client.get(test_case.first_object_response.data['url'])
    test_case.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)

    response = test_case.client.delete(test_case.first_object_response.data['url'])
    test_case.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code, response.data)