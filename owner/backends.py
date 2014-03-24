# -*- coding: utf-8 -*-
from rest_framework import filters


# TODO Improve filter to get owner and children data
class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_root_node():
            return queryset.filter(owner=request.user)
        else:
            return queryset.filter(children=request.user)