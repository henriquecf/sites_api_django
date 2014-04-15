# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.account.models import AccountUser, Account, AccountGroup, AuthorRestriction


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
    def get_fields(self):
        fields = super(UserSerializer, self).get_fields()
        fields['groups'].queryset = fields['groups'].queryset.filter(
            accountgroup__account=self.context['request'].user.accountuser.account)
        return fields

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
    assign_permissions = serializers.HyperlinkedIdentityField(label=_('assign permissions'),
                                                              view_name='accountgroup-assign-permissions')
    unassign_permissions = serializers.HyperlinkedIdentityField(label=_('unassign permissions'),
                                                                view_name='accountgroup-unassign-permissions')

    class Meta:
        model = AccountGroup


class AuthorRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    def get_fields(self):
        fields = super(AuthorRestrictionSerializer, self).get_fields()
        fields['user'].queryset = fields['user'].queryset.filter(
            accountuser__account=self.context['request'].user.accountuser.account)
        fields['group'].queryset = fields['group'].queryset.filter(
            accountgroup__account=self.context['request'].user.accountuser.account)
        return fields

    user = serializers.PrimaryKeyRelatedField(label=_('user'), blank=True)
    permission = serializers.PrimaryKeyRelatedField(label=_('permission'))
    group = serializers.PrimaryKeyRelatedField(label=_('group'), blank=True)

    class Meta:
        model = AuthorRestriction
