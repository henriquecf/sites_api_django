# -*- coding: utf-8 -*-
from django.utils.text import slugify
from rest_framework import status
from resource.routines import test_resource_serializer_hyperlinked_fields_routine


def test_slug_is_slugified_title_routine(test_case, slug_repeat_number='-2'):
    response = test_case.client.post(test_case.url, test_case.data)
    test_case.assertEqual(response.data['slug'], slugify(response.data['title']) + slug_repeat_number,
                          'Slug is not slugified title')


def test_slug_is_unique_routine(test_case):
    test_slug_is_slugified_title_routine(test_case, slug_repeat_number='-2')
    test_slug_is_slugified_title_routine(test_case, slug_repeat_number='-3')
    test_slug_is_slugified_title_routine(test_case, slug_repeat_number='-4')


def test_has_author_routine(test_case):
    test_case.assertIn('creator', test_case.first_object_response.data, 'Response has no field "creator"')


def test_is_published_default_true_routine(test_case):
    test_case.assertIn('is_published', test_case.first_object_response.data, 'Response has no field "is_published"')
    test_case.assertTrue(test_case.first_object_response.data['is_published'],
                         'Is_published default value must be True')


def get_action_response(test_case, action_name, status_code=status.HTTP_200_OK):
    action_url = test_case.first_object_response.data[action_name]
    response = test_case.client.post(action_url)
    test_case.assertEqual(response.status_code, status_code)
    return response


def test_unpublish_routine(test_case):
    response = get_action_response(test_case, 'unpublish')
    test_case.assertFalse(response.data['is_published'], 'Is_published return must be False')


def test_publish_routine(test_case):
    response = get_action_response(test_case, 'publish')
    test_case.assertTrue(response.data['is_published'], 'Is_published return must be True')


def test_publication_serializer_hyperlinked_fields_routine(test_case, fields):
    test_resource_serializer_hyperlinked_fields_routine(test_case, fields)


