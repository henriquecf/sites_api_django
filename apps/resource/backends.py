# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import filters, permissions
from apps.resource.models import AuthorRestriction


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


class SiteDomainFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        domain = request.META.get('HTTP_HOST')
        if not domain:
            domain = request.META.get('SERVER_NAME')
        return queryset.filter(sites__domain=domain)


class AuthorRestrictionBackend(filters.BaseFilterBackend):
    """This filter analise the user and its permissions.

    If the user is a superuser, he has access to the whole model.
    Else if the user is staff, meaning he is an administrator of the account, he has access every object related to that
    account.
    Else, the global permissions are checked:
        If the user has global permission, he has access to the account data.
        Else, he has access just to his data.
    """

    def filter_queryset(self, request, queryset, view):
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
            try:
                creator_restriction = AuthorRestriction.objects.filter(
                    Q(permission__content_type__app_label=app_label), Q(permission__codename=codename),
                    Q(user=request.user) | Q(group__in=request.user.groups.all()))[0]
            except ObjectDoesNotExist:
                queryset = queryset.filter(author=request.user)
            except IndexError:
                queryset = queryset.filter(author=request.user)
            else:
                queryset = queryset.filter(author__in=creator_restriction.filter_values.split(','))
            return queryset
        else:
            return queryset.filter(author=request.user)


class ResourceFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user.user.owner)