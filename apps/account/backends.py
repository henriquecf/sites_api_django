# -*- coding: utf-8 -*-
from rest_framework import filters


class AccountFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(account=request.user.user.account)