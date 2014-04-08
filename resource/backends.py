# -*- coding: utf-8 -*-
from rest_framework import filters, permissions
from account.backends import custom_permissions_map


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
    """Customization of DjangoModelPermissions including restriction for GET calls in the API."""
    perms_map = custom_permissions_map


class ResourceFilterBackend(filters.BaseFilterBackend):
    """This filter analise the user and its permissions.

    If the user is a superuser, he has access to the whole model.
    Else if the user is staff, meaning he is an administrator of the account, he has access every object related to that
    account.
    Else, the global permissions are checked:
        If the user has global permission, he has access to the account data.
        Else, he has access just to his data.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        elif request.user.is_staff:
            return queryset.filter(account=request.user.accountuser.account)
        else:
            model_cls = getattr(view, 'model', None)

            kwargs = {
                'app_label': model_cls._meta.app_label,
                'model_name': model_cls._meta.model_name
            }
            try:
                permission = custom_permissions_map[request.method][0] % kwargs
            except KeyError:
                permission = None
            if permission and request.user.accountuser.has_filter_permission(permission):
                return queryset.filter(account=request.user.accountuser.account)
            else:
                return queryset.filter(creator=request.user)