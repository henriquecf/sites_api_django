# -*- coding: utf-8 -*-
from rest_framework import filters, permissions

from apps.account.backends import custom_permissions_map


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
    """Customization of DjangoModelPermissions including restriction for GET calls in the API."""
    perms_map = custom_permissions_map


class SiteDomainFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        domain = request.META.get('HTTP_HOST')
        if not domain:
            domain = request.META.get('SERVER_NAME')
        return queryset.filter(sites__domain=domain)