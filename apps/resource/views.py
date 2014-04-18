from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site as ContribSite
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from apps.account.exceptions import BadRequestValidationError

from apps.resource.models import Resource, Site, User, Group
from apps.resource.serializers import ResourceSerializer, AccountSiteSerializer, UserSerializer, \
    GroupSerializer, SiteSerializer


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
            obj.account
        except ObjectDoesNotExist:
            obj.author = self.request.user
            obj.account = self.request.user.user.account

    def post_save(self, obj, created=False):
        if not obj.sites.all():
            domain = self.request.META.get('HTTP_HOST')
            if not domain:
                domain = self.request.META.get('SERVER_NAME')
            site, created = ContribSite.objects.get_or_create(domain=domain)
            try:
                Site.objects.get(site=site, account=obj.account)
            except ObjectDoesNotExist:
                Site.objects.create(site=site, account=obj.account, author=obj.author)
            obj.sites.add(site)


class AccountSiteRetrieveAPIViewSet(ReadOnlyModelViewSet):
    model = Site
    serializer_class = AccountSiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()

    def get_queryset(self):
        return super(AccountSiteRetrieveAPIViewSet, self).get_queryset().filter(
            account=self.request.user.user.account)


class UserViewSet(ResourceViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        """Returns a filtered queryset when the request user is not a superuser.

        Users must access only objects related to his account, unless they are superusers.
        """
        queryset = super(UserViewSet, self).get_queryset()
        try:
            account = self.request.user.user.account
        except ObjectDoesNotExist:
            account = self.request.user.account
        return queryset.filter(account=account)


class GroupViewSet(ResourceViewSet):
    model = Group
    serializer_class = GroupSerializer
    search_fields = ['role']

    def get_queryset(self):
        queryset = super(GroupViewSet, self).get_queryset()
        return queryset.filter(account=self.request.user.user.account)

    def pre_save(self, obj):
        try:
            Group.objects.get(account=self.request.user.user.account, role=obj.role)
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
        return Response(data={'assigned_permissions': permissions_to_unassign})


class SiteViewSet(ReadOnlyModelViewSet):
    model = ContribSite
    serializer_class = SiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()

    def get_queryset(self):
        return super(SiteViewSet, self).get_queryset().filter(site__account=self.request.user.user.account)