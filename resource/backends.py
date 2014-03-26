# -*- coding: utf-8 -*-
from rest_framework import filters, permissions

# TODO Refactor this into separate sets
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


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
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


class ResourcePermissionFilterBackend(filters.BaseFilterBackend):
    """
    This filter analise the user and its permissions.
    If the user has global permission for the method, the filter is applied to the resource.
    If the user has non global permission for the method, the filter is applied to the children.
    The only exception is when the user is the resource itself. In this case, the resource filter applies anyway.
    """
    # TODO The the way comparing has_perm to compare directly with separate sets and eliminate get_required_permissions
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
            return queryset.filter(creator=request.user)


class IsResourceFilterBackend(filters.BaseFilterBackend):
    """
    Filter for shared databases.
    Allow just to see data he owns.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(creator=request.user)


class IsResourceChildrenFilterBackend(filters.BaseFilterBackend):
    """
    Filter for shared databases.
    Filter that only allows owners to see its data and its children data,
    and children to see just their data
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(creator=request.user)