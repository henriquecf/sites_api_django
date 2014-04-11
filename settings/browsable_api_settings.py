# -*- coding: utf-8 -*-
from settings.dev_settings import *

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'resource.backends.CustomDjangoModelPermissions',
    ),
    'DEFAULT_FILTER_BACKENDS': OTHER_FILTERS + DJANGO_FILTERS
}