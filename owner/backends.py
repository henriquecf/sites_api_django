# -*- coding: utf-8 -*-
from rest_framework import filters, permissions

custom_permissions_map = {
    'GET': ['%(app_label)s.read_%(model_name)s', '%(app_label)s.read_global_%(model_name)s'],
    'OPTIONS': ['%(app_label)s.read_%(model_name)s', '%(app_label)s.read_global_%(model_name)s'],
    'HEAD': ['%(app_label)s.read_%(model_name)s', '%(app_label)s.read_global_%(model_name)s'],
    'POST': ['%(app_label)s.add_%(model_name)s', '%(app_label)s.add_global_%(model_name)s'],
    'PUT': ['%(app_label)s.change_%(model_name)s', '%(app_label)s.change_global_%(model_name)s'],
    'PATCH': ['%(app_label)s.change_%(model_name)s', '%(app_label)s.change_global_%(model_name)s'],
    'DELETE': ['%(app_label)s.delete_%(model_name)s', '%(app_label)s.delete_global_%(model_name)s'],
}


def get_required_permissions(method, model_cls):
    kwargs = {
        'app_label': model_cls._meta.app_label,
        'model_name': permissions.get_model_name(model_cls)
    }
    return [perm % kwargs for perm in custom_permissions_map[method]]


class DjangoModelCustomPermissions(permissions.DjangoModelPermissions):
    """
    Customization of DjangoModelPermissions including restriction for GET calls in the API.
    For this restriction to apply, the read permission must be in the model.
    """
    perms_map = custom_permissions_map

    def has_permission(self, request, view):
        model_cls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if model_cls is None and getattr(view, '_ignore_model_permissions', False):
            return True

        assert model_cls, ('Cannot apply DjangoModelPermissions on a view that'
                           ' does not have `.model` or `.queryset` property.')

        perms = self.get_required_permissions(request.method, model_cls)

        non_global_permission = perms[0]
        global_permission = perms[1]

        return (request.user and
                (request.user.is_authenticated() or not self.authenticated_users_only) and
                (request.user.has_perm(global_permission) or request.user.has_perm(non_global_permission)))


class OwnerPermissionFilterBackend(filters.BaseFilterBackend):
    """
    This filter analise the user and its permissions.
    If the user has global permission for the method, the filter is applied to the owner.
    If the user has non global permission for the method, the filter is applied to the children.
    The only exception is when the user is the owner itself. In this case, the owner filter applies anyway.
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if user.is_root_node():
            return queryset.filter(owner=user)
        else:
            model_cls = getattr(view, 'model', None)
            queryset = getattr(view, 'queryset', None)

            if model_cls is None and queryset is not None:
                model_cls = queryset.model
            required_permissions = get_required_permissions(request.method, model_cls)
            global_permission = required_permissions[1]
            if user.has_perm(global_permission):
                return queryset.filter(owner=user)
            else:
                return queryset.filter(children=user)


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