from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from apps.account.exceptions import BadRequestValidationError

from apps.resource.models import Resource, AccountSite, AccountUser, Group
from apps.resource.serializers import ResourceSerializer, AccountSiteSerializer, AccountUserSerializer, \
    AccountGroupSerializer, SiteSerializer


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
            obj.account = self.request.user.accountuser.account

    def post_save(self, obj, created=False):
        if not obj.sites.all():
            domain = self.request.META.get('HTTP_HOST')
            if not domain:
                domain = self.request.META.get('SERVER_NAME')
            site, created = Site.objects.get_or_create(domain=domain)
            account_site, created2 = AccountSite.objects.get_or_create(site=site, account=obj.account)
            obj.sites.add(site)


class AccountSiteRetrieveAPIViewSet(ReadOnlyModelViewSet):
    model = AccountSite
    serializer_class = AccountSiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()

    def get_queryset(self):
        return super(AccountSiteRetrieveAPIViewSet, self).get_queryset().filter(
            account=self.request.user.accountuser.account)


class AccountUserViewSet(ModelViewSet):
    model = AccountUser
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()
    serializer_class = AccountUserSerializer

    def get_queryset(self):
        """Returns a filtered queryset when the request user is not a superuser.

        Users must access only objects related to his account, unless they are superusers.
        """
        queryset = super(AccountUserViewSet, self).get_queryset()
        try:
            account = self.request.user.accountuser.account
        except ObjectDoesNotExist:
            account = self.request.user.account
        return queryset.filter(account=account)

    def pre_save(self, obj):
        """

        Relates the account of the request user to the object.
        Checks if the request user already has an accountuser. Returns an exception in true case, or relates the user to
        the object otherwise.
        Warning: this method will work only for the owner of the account, the way it is implemented here.
        """
        obj.account = self.request.user.account
        try:
            AccountUser.objects.get(user=self.request.user)
            raise BadRequestValidationError(_('You can create just one user account.'))
        except ObjectDoesNotExist:
            obj.user = self.request.user


class AccountGroupViewSet(ModelViewSet):
    model = Group
    serializer_class = AccountGroupSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = ['role']

    def get_queryset(self):
        queryset = super(AccountGroupViewSet, self).get_queryset()
        return queryset.filter(account=self.request.user.accountuser.account)

    def pre_save(self, obj):
        try:
            Group.objects.get(account=self.request.user.accountuser.account, role=obj.role)
            raise BadRequestValidationError(_('Role field is unique. Please insert another name.'))
        except ObjectDoesNotExist:
            obj.account = self.request.user.accountuser.account

    @action()
    def assign_permissions(self, request, *args, **kwargs):
        accountgroup = self.get_object()
        try:
            permissions_to_assign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_assign:
            accountgroup.group.permissions.add(permission)
        return Response(data={'assigned_permissions': permissions_to_assign})

    @action()
    def unassign_permissions(self, request, *args, **kwargs):
        accountgroup = self.get_object()
        try:
            permissions_to_unassign = request.DATA['permissions']
        except KeyError:
            return Response(
                data={'detail': _('You must define the permissions to assign through dict key "permissions".')},
                status=status.HTTP_400_BAD_REQUEST)
        for permission in permissions_to_unassign:
            accountgroup.group.permissions.remove(permission)
        return Response(data={'assigned_permissions': permissions_to_unassign})


class SiteViewSet(ReadOnlyModelViewSet):
    model = Site
    serializer_class = SiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()

    def get_queryset(self):
        return super(SiteViewSet, self).get_queryset().filter(
            accountsite__account=self.request.user.accountuser.account)