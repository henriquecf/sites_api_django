import datetime
from django.db.models import Q
from django.contrib.auth import hashers
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, filters, generics
from account.exceptions import BadRequestValidationError
from account.serializers import (
    AccountUserSerializer,
    UserSerializer,
    UserCreateChangeSerializer,
    AccountSerializer,
    AccountGroupSerializer,
    FilterRestrictionSerializer,
)
from account.models import Account, AccountUser, AccountGroup, FilterRestriction


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        """Filter only user resources or get all if user is superuser."""
        if self.request.user.is_superuser:
            return super(AccountViewSet, self).get_queryset()
        else:
            return super(AccountViewSet, self).get_queryset().filter(owner=self.request.user)

    def pre_save(self, obj):
        """Create an account to a user only if he does not have one yet."""
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        try:
            Account.objects.get(owner=self.request.user)
            raise BadRequestValidationError('You already have an account and can not create another one.')
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
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(account=self.request.user.accountuser.account)

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
            raise BadRequestValidationError('You can create just one user account')
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
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(accountuser__account=self.request.user.accountuser.account)

    def get_serializer_class(self):
        """Checks the request method to see which serializer is returned.

        If it is a "GET" method, the serializer does not have the password field. Otherwise, it has the password field.
        """
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserCreateChangeSerializer

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
        user = self.request.user
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(account=user.accountuser.account)

    def pre_save(self, obj):
        try:
            AccountGroup.objects.get(account=self.request.user.accountuser.account, role=obj.role)
            raise BadRequestValidationError('Role field is unique. Please insert another name.')
        except ObjectDoesNotExist:
            obj.account = self.request.user.accountuser.account


class FilterRestrictionViewSet(ModelViewSet):
    model = FilterRestriction
    serializer_class = FilterRestrictionSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        queryset = super(FilterRestrictionViewSet, self).get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(
                Q(accountuser__account=user.accountuser.account) | Q(accountgroup__account=user.accountuser.account))

    # TODO This viewset (or the serializer) need to assign the permission to the user or group if not assigned yet
    def pre_save(self, obj):
        try:
            account = obj.accountuser.account
        except AttributeError:
            try:
                account = obj.accountgroup.account
            except AttributeError:
                raise BadRequestValidationError('Accountuser or accountgroup is required.')

        if account != self.request.user.accountuser.account:
            raise BadRequestValidationError('You can not alter other account permissions.')
        else:
            super(FilterRestrictionViewSet, self).pre_save(obj)


class PermissionDetailView(generics.RetrieveAPIView):
    model = Permission
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()


class GroupDetailView(generics.RetrieveAPIView):
    model = Group
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()