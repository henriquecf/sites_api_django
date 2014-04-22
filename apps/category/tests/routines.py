# -*- coding: utf-8 -*-
from copy import copy
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from rest_framework import status


def test_add_category_routine(test_case, name='Category 1'):
    data2 = copy(test_case.data)
    model_content_type = ContentType.objects.get_for_model(test_case.model)
    category_data = {
        'name': name,
        'model': model_content_type.id,
    }
    category_url = reverse('category-list')
    response = test_case.client.post(category_url, category_data)
    cat1_url = response.data['url']
    data2.update({'categories': [cat1_url]})
    response2 = test_case.client.post(test_case.url, data2)
    test_case.assertEqual(response2.status_code, status.HTTP_201_CREATED)
    try:
        model_categories = response2.data['categories']
    except KeyError:
        model_categories = None
    test_case.assertEqual(model_categories, [cat1_url],
                          'Field categories not found in model "{0}"'.format(test_case.model._meta.model_name))


def test_filter_categories(test_case):
    test_add_category_routine(test_case)
    category_filter = {'categories': 'Category 1'}
    response = test_case.client.get(test_case.url, category_filter)
    test_case.assertEqual(1, response.data['count'], response.data)

    test_add_category_routine(test_case, name='Category 2')
    category_filter2 = {'categories': 'Category 2'}
    response2 = test_case.client.get(test_case.url, category_filter2)
    test_case.assertEqual(1, response2.data['count'], response2.data)

    category_filter3 = {'categories': ['Category 1', 'Category 2']}
    response3 = test_case.client.get(test_case.url, category_filter3)
    # TODO Check why multiple filter is not working
    #test_case.assertEqual(2, response3.data['count'], response3.data)