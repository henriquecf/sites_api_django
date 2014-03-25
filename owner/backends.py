# -*- coding: utf-8 -*-
from rest_framework import filters, permissions

custom_permissions_map = {
    'GET': ['%(app_label)s.read_%(model_name)s'],
    'OPTIONS': [],
    'HEAD': [],
    'POST': ['%(app_label)s.add_%(model_name)s'],
    'PUT': ['%(app_label)s.change_%(model_name)s'],
    'PATCH': ['%(app_label)s.change_%(model_name)s'],
    'DELETE': ['%(app_label)s.delete_%(model_name)s'],
}


class DjangoModelCustomPermissions(permissions.DjangoModelPermissions):
    perms_map = custom_permissions_map


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter for shared databases.
    Allow just to see data he owns.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)


class IsOwnerChildrenFilterBackend(filters.BaseFilterBackend):
    """
    Filter for shared databases.
    Filter that only allows owners to see its data and its children data,
    and children to see just their data
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_root_node():
            return queryset.filter(owner=request.user)
        else:
            return queryset.filter(children=request.user)