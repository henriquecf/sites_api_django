from django.contrib.auth import hashers
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, permissions

from .serializers import AccountUserSerializer, UserSerializer, UserCreateChangeSerializer
from .models import AccountUser


class AccountUserViewSet(ModelViewSet):
    model = AccountUser
    permission_classes = (
        permissions.IsAdminUser,
    )
    serializer_class = AccountUserSerializer

    def pre_save(self, obj):
        print('Ok')
        obj.account = self.request.user.get_profile().account
        obj.user = self.request.user


class UserViewSet(ModelViewSet):
    model = User
    search_fields = ('username', 'email')
    filter_backends = (
        filters.SearchFilter,
    )
    permission_classes = (
        permissions.IsAdminUser,
    )

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(accountuser__account=self.request.user.get_profile().account)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserCreateChangeSerializer

    def pre_save(self, obj):
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)