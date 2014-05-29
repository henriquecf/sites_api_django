# -*- coding: utf-8 -*-
from settings.dev import *

ALLOWED_HOSTS = ['http://localhost:63342/']

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.UnicodeJSONRenderer',
        'rest_framework.renderers.HTMLFormRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'apps.resource.backends.CustomDjangoModelPermissions',
    ),
    'DEFAULT_FILTER_BACKENDS': OTHER_FILTERS + DJANGO_FILTERS
}