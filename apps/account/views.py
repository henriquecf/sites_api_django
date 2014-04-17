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
    UserSerializer,
    AccountSerializer,
    AuthorRestrictionSerializer,
    RestrictedOwnerUserSerializer,
)
from apps.account.models import Account, AuthorRestriction
from apps.resource.models import AccountUser


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


class AuthorRestrictionViewSet(ModelViewSet):
    model = AuthorRestriction
    serializer_class = AuthorRestrictionSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        queryset = super(AuthorRestrictionViewSet, self).get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(
                Q(user__accountuser__account=user.accountuser.account) | Q(
                    group__group__account=user.accountuser.account))

    def pre_save(self, obj):
        try:
            account = obj.user.accountuser.account
        except AttributeError:
            try:
                account = obj.group.group.account
            except AttributeError:
                raise BadRequestValidationError(_('You must specify either User or Group field.'))

        if account != self.request.user.accountuser.account:
            raise BadRequestValidationError(_('You can not alter other account permissions.'))
        else:
            super(AuthorRestrictionViewSet, self).pre_save(obj)


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

    def get_queryset(self):
        return super(GroupViewSet, self).get_queryset().filter(
            accountgroup__account=self.request.user.accountuser.account)