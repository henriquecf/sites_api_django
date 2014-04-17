# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group as AuthGroup
from rest_framework import serializers
from apps.resource.models import AccountSite, Resource, Group, AccountUser


class AuthGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthGroup
        fields = ('permissions',)


class ResourceSerializer(serializers.HyperlinkedModelSerializer):

    def get_fields(self):
        fields = super(ResourceSerializer, self).get_fields()
        fields['sites'].queryset = fields['sites'].queryset.filter(
            accountsite__account=self.context['request'].user.accountuser.account)
        return fields

    class Meta:
        model = Resource
        read_only_fields = ('author', 'account')


class AccountSiteSerializer(serializers.HyperlinkedModelSerializer):
    site = serializers.PrimaryKeyRelatedField(label=_('site'), read_only=True)

    class Meta:
        model = AccountSite


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(label=_('account'), view_name='account-detail', read_only=True)
    group = AuthGroupSerializer(read_only=True)
    assign_permissions = serializers.HyperlinkedIdentityField(label=_('assign permissions'),
                                                              view_name='group-assign-permissions')
    unassign_permissions = serializers.HyperlinkedIdentityField(label=_('unassign permissions'),
                                                                view_name='group-unassign-permissions')

    class Meta:
        model = Group


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(label=_('user'), view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(label=_('account'), view_name='account-detail', read_only=True)

    class Meta:
        model = AccountUser


class SiteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Site