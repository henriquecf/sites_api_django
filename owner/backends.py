# -*- coding: utf-8 -*-
from rest_framework import filters


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