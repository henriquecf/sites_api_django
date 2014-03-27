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
    """
    Customization of DjangoModelPermissions including restriction for GET calls in the API.
    For this restriction to apply, the read permission must be in the model.
    """
    perms_map = custom_permissions_map


class ResourceFilterBackend(filters.BaseFilterBackend):
    """
    This filter analise the user and its permissions.
    If the user has global permission for the method, the filter is applied to the resource.
    If the user has non global permission for the method, the filter is applied to the children.
    The only exception is when the user is the resource itself. In this case, the resource filter applies anyway.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset.filter(account=request.user.accountuser.account)
        else:
            return queryset.filter(creator=request.user)