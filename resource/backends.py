# -*- coding: utf-8 -*-
from rest_framework import filters, permissions


custom_permissions_map = {
    'GET': ['%(app_label)s.view_%(model_name)s'],
    'OPTIONS': [],
    'HEAD': [],
    'POST': ['%(app_label)s.add_%(model_name)s'],
    'PUT': ['%(app_label)s.change_%(model_name)s'],
    'PATCH': ['%(app_label)s.change_%(model_name)s'],
    'DELETE': ['%(app_label)s.delete_%(model_name)s'],
}


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
    """Customization of DjangoModelPermissions including restriction for GET calls in the API."""
    perms_map = custom_permissions_map


class ResourceFilterBackend(filters.BaseFilterBackend):
    """This filter analise the user and its permissions.

    If the user is a superuser, he has access to the whole model.
    Else if the user is staff, meaning he is an administrator of the account, he has access every object related to that
    account.
    Else he has just access to the objects he created.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        elif request.user.is_staff:
            return queryset.filter(account=request.user.accountuser.account)
        else:
            return queryset.filter(creator=request.user)