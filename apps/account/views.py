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
from apps.resource.models import User


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
                Q(user__user__account=user.user.account) | Q(
                    group__group__account=user.user.account))

    def pre_save(self, obj):
        try:
            account = obj.user.user.account
        except AttributeError:
            try:
                account = obj.group.group.account
            except AttributeError:
                raise BadRequestValidationError(_('You must specify either User or Group field.'))

        if account != self.request.user.user.account:
            raise BadRequestValidationError(_('You can not alter other account permissions.'))
        else:
            super(AuthorRestrictionViewSet, self).pre_save(obj)


class PermissionViewSet(ReadOnlyModelViewSet):
    model = Permission
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()