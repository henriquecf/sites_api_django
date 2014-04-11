# -*- coding: utf-8 -*-
from rest_framework import filters
from account.models import FilterRestriction


custom_permissions_map = {
    'GET': ['%(app_label)s.view_%(model_name)s'],
    'OPTIONS': [],
    'HEAD': [],
    'POST': ['%(app_label)s.add_%(model_name)s'],
    'PUT': ['%(app_label)s.change_%(model_name)s'],
    'PATCH': ['%(app_label)s.change_%(model_name)s'],
    'DELETE': ['%(app_label)s.delete_%(model_name)s'],
}


class FilterRestrictionBackend(filters.BaseFilterBackend):
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
            if permission and request.user.has_perm(permission):
                app_label, codename = permission.split('.')
                restriction_filters = FilterRestriction.objects.filter(permission__content_type__app_label=app_label,
                                                                       permission__codename=codename)
                for filter_restriction in restriction_filters:
                    queryset = queryset.filter(
                        **{'{0}__in'.format(filter_restriction.filter_field): filter_restriction.values.split(',')})
                else:
                    queryset = queryset.filter(account=request.user.accountuser.account)
                return queryset
            else:
                return queryset.filter(creator=request.user)