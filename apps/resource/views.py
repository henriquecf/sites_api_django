from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site as ContribSite
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.resource.exceptions import BadRequestValidationError
from apps.resource.models import Resource, Site, User, Group, AuthorRestriction
from apps.resource.serializers import ResourceSerializer, UserSerializer, \
    GroupSerializer, AuthorRestrictionSerializer
from apps.resource.backends import AuthorRestrictionBackend, SiteDomainFilterBackend, ResourceFilterBackend


class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/form.html'

    def get_success_url(self):
        """Checks if there is a URL to redirect through the key "next". Goes to root URL otherwise."""
        try:
            return self.request.GET['next']
        except KeyError:
            return '/'

    def form_valid(self, form):
        """Authenticates the user and logs him in."""
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(UserLoginView, self).form_valid(form)


class ResourceViewSet(viewsets.ModelViewSet):
    model = Resource
    serializer_class = ResourceSerializer

    def pre_save(self, obj):
        """Checks if there is a author and account for the resource.

        Does nothing if it has, assigns the request user and its account to the object otherwise.
        """
        try:
            obj.author
            obj.owner
        except ObjectDoesNotExist:
            obj.author = self.request.user
            obj.owner = self.request.user.user.owner

    def post_save(self, obj, created=False):
        if not obj.sites.all():
            domain = self.request.META.get('HTTP_HOST')
            if not domain:
                domain = self.request.META.get('SERVER_NAME')
            site, created = ContribSite.objects.get_or_create(domain=domain)
            try:
                Site.objects.get(site=site, owner=obj.owner)
            except ObjectDoesNotExist:
                Site.objects.create(site=site, owner=obj.owner, author=obj.author)
            obj.sites.add(site)


class UserViewSet(ResourceViewSet):
    model = User
    serializer_class = UserSerializer

    @action()
    def assign_groups(self, request, *args, **kwargs):
        user = self.get_object().user
        if user == self.get_object().owner:
            return Response(
                data={'detail': _('You can not alter owner groups.')},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            groups_to_assign = request.DATA['groups']
        except KeyError:
            return Response(
                data={'detail': _('You must define the groups through dict key "groups".')},
                status=status.HTTP_400_BAD_REQUEST)
        for group in groups_to_assign:
            user.groups.add(group)
        return Response(data={'assigned_groups': groups_to_assign})

    @action()
    def unassign_groups(self, request, *args, **kwargs):
        user = self.get_object().user
        if user == self.get_object().owner:
            return Response(
                data={'detail': _('You can not alter owner groups.')},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            groups_to_unassign = request.DATA['groups']
        except KeyError:
            return Response(
                data={'detail': _('You must define the groups through dict key "groups".')},
                status=status.HTTP_400_BAD_REQUEST)
        for group in groups_to_unassign:
            user.groups.remove(group)
        return Response(data={'unassigned_groups': groups_to_unassign})

    @action()
    def assign_permissions(self, request, *args, **kwargs):
        user = self.get_object().user
        if user == self.get_object().owner:
            return Response(
                data={'detail': _('You can not alter owner permissions.')},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            permissions_to_assign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_assign:
            user.user_permissions.add(permission)
        return Response(data={'assigned_permissions': permissions_to_assign})

    @action()
    def unassign_permissions(self, request, *args, **kwargs):
        user = self.get_object().user
        if user == self.get_object().owner:
            return Response(
                data={'detail': _('You can not alter owner permissions.')},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            permissions_to_unassign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions to assign through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_unassign:
            user.user_permissions.remove(permission)
        return Response(data={'unassigned_permissions': permissions_to_unassign})


class GroupViewSet(ResourceViewSet):
    model = Group
    serializer_class = GroupSerializer
    search_fields = ['role']

    def pre_save(self, obj):
        try:
            Group.objects.get(owner=self.request.user.user.owner, role=obj.role)
            raise BadRequestValidationError(_('Role field is unique. Please insert another name.'))
        except ObjectDoesNotExist:
            super(GroupViewSet, self).pre_save(obj)

    @action()
    def assign_permissions(self, request, *args, **kwargs):
        group = self.get_object()
        try:
            permissions_to_assign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_assign:
            group.group.permissions.add(permission)
        return Response(data={'assigned_permissions': permissions_to_assign})

    @action()
    def unassign_permissions(self, request, *args, **kwargs):
        group = self.get_object()
        try:
            permissions_to_unassign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions to assign through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_unassign:
            group.group.permissions.remove(permission)
        return Response(data={'unassigned_permissions': permissions_to_unassign})


class AuthorRestrictionViewSet(ResourceViewSet):
    model = AuthorRestriction
    serializer_class = AuthorRestrictionSerializer

    def pre_save(self, obj):
        try:
            owner = obj.user.user.owner
        except AttributeError:
            try:
                owner = obj.group.group.owner
            except AttributeError:
                raise BadRequestValidationError(_('You must specify either User or Group field.'))

        if owner != self.request.user.user.owner:
            raise BadRequestValidationError(_('You can not alter other account permissions.'))
        else:
            super(AuthorRestrictionViewSet, self).pre_save(obj)