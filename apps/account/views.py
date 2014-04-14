import datetime
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import hashers
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions, filters

from apps.account.exceptions import BadRequestValidationError
from apps.account.serializers import (
    AccountUserSerializer,
    UserSerializer,
    AccountSerializer,
    AccountGroupSerializer,
    CreatorRestrictionSerializer,
    RestrictedOwnerUserSerializer,
)
from apps.account.models import Account, AccountUser, AccountGroup, CreatorRestriction


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        """Filter only user resources or get all if user is superuser."""
        return super(AccountViewSet, self).get_queryset().filter(owner=self.request.user)

    def pre_save(self, obj):
        """Create an account to a user only if he does not have one yet."""
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        try:
            Account.objects.get(owner=self.request.user)
            raise BadRequestValidationError(_('You already have an account and can not create another one.'))
        except ObjectDoesNotExist:
            obj.owner = self.request.user


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
            raise BadRequestValidationError(_('You can create just one user account'))
        except ObjectDoesNotExist:
            obj.user = self.request.user


class UserViewSet(ModelViewSet):
    """

    The fields username and email are searchable in this viewset.
    This viewset can be accessed just by admin users (staff or superuser).
    """
    model = User
    search_fields = ('username', 'email')
    filter_backends = (
        filters.SearchFilter,
    )
    permission_classes = (
        permissions.IsAdminUser,
    )

    def get_queryset(self):
        """

        If the request user is super user, the whole model can be accessed.
        Otherwise a filter is applied to return just the users related to same account as the request user.
        """
        queryset = super(UserViewSet, self).get_queryset()
        return queryset.filter(accountuser__account=self.request.user.accountuser.account)

    def get_serializer_class(self):
        """In the case the user is the owner of the account, he must not be able to change his user_permissions, groups
        or is_staff status
        """
        try:
            obj = self.get_object()
        except:
            pass
        else:
            if obj == self.request.user.accountuser.account.owner:
                return RestrictedOwnerUserSerializer

        return UserSerializer

    def pre_save(self, obj):
        """Hash the password if not hashed yet."""
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)

    def post_save(self, obj, created=False):
        """Creates an accountuser for the created user, which will be related to same account as the request user."""
        if self.request.method == 'POST':
            accountuser = AccountUser.objects.create(user=obj, account=self.request.user.accountuser.account)
            obj.accountuser = accountuser
            obj.save()


class AccountGroupViewSet(ModelViewSet):
    model = AccountGroup
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
            AccountGroup.objects.get(account=self.request.user.accountuser.account, role=obj.role)
            raise BadRequestValidationError(_('Role field is unique. Please insert another name.'))
        except ObjectDoesNotExist:
            obj.account = self.request.user.accountuser.account


class CreatorRestrictionViewSet(ModelViewSet):
    model = CreatorRestriction
    serializer_class = CreatorRestrictionSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        queryset = super(CreatorRestrictionViewSet, self).get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(
                Q(user__accountuser__account=user.accountuser.account) | Q(group__accountgroup__account=user.accountuser.account))

    def pre_save(self, obj):
        try:
            account = obj.user.accountuser.account
        except AttributeError:
            try:
                account = obj.group.accountgroup.account
            except AttributeError:
                raise BadRequestValidationError(_('You must specify either User or Group field.'))

        if account != self.request.user.accountuser.account:
            raise BadRequestValidationError(_('You can not alter other account permissions.'))
        else:
            super(CreatorRestrictionViewSet, self).pre_save(obj)


class PermissionViewSet(ReadOnlyModelViewSet):
    model = Permission
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()


class GroupViewSet(ReadOnlyModelViewSet):
    model = Group
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()