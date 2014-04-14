# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.account.models import AccountUser, Account, AccountGroup, FilterRestriction


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(label=_('owner'), view_name='user-detail', read_only=True)

    class Meta:
        model = Account


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(label=_('user'), view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(label=_('account'), view_name='account-detail', read_only=True)

    class Meta:
        model = AccountUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Must be called when a non safe method is being requested."""
    email = serializers.EmailField(required=True)
    accountuser = serializers.HyperlinkedRelatedField(view_name='accountuser-detail', read_only=True)

    class Meta:
        model = User
        exclude = ['is_superuser']
        read_only_fields = ('date_joined', 'last_login', 'is_active')
        write_only_fields = ('password',)


class RestrictedOwnerUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('date_joined', 'last_login', 'is_active', 'is_staff', 'user_permissions', 'groups')


class AccountGroupSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(label=_('account'), view_name='account-detail', read_only=True)
    group = serializers.HyperlinkedRelatedField(label=_('group'), view_name='group-detail', read_only=True)

    class Meta:
        model = AccountGroup


class FilterRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(blank=True)
    permission = serializers.PrimaryKeyRelatedField()
    group = serializers.PrimaryKeyRelatedField(blank=True)

    class Meta:
        model = FilterRestriction