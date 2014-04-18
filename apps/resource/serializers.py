# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.contrib.sites.models import Site as ContribSite
from django.contrib.auth.models import Group as AuthGroup
from rest_framework import serializers
from apps.resource.models import Site, Resource, Group, User, AuthorRestriction
from apps.account.serializers import UserSerializer as AuthUserSerializer


class AuthGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthGroup
        fields = ('permissions',)


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthUserSerializer(read_only=True)

    def get_fields(self):
        fields = super(ResourceSerializer, self).get_fields()
        fields['sites'].queryset = fields['sites'].queryset.filter(
            site__account=self.context['request'].user.user.account)
        return fields

    class Meta:
        model = Resource
        read_only_fields = ('account',)


class AccountSiteSerializer(serializers.HyperlinkedModelSerializer):
    site = serializers.PrimaryKeyRelatedField(label=_('site'), read_only=True)

    class Meta:
        model = Site


class GroupSerializer(ResourceSerializer):
    group = AuthGroupSerializer(read_only=True)
    assign_permissions = serializers.HyperlinkedIdentityField(label=_('assign permissions'),
                                                              view_name='group-assign-permissions')
    unassign_permissions = serializers.HyperlinkedIdentityField(label=_('unassign permissions'),
                                                                view_name='group-unassign-permissions')

    class Meta(ResourceSerializer.Meta):
        model = Group


class UserSerializer(ResourceSerializer):
    user = AuthUserSerializer()

    class Meta(ResourceSerializer.Meta):
        model = User


class SiteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ContribSite


class AuthorRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    def get_fields(self):
        fields = super(AuthorRestrictionSerializer, self).get_fields()
        fields['user'].queryset = fields['user'].queryset.filter(
            user__account=self.context['request'].user.user.account)
        fields['group'].queryset = fields['group'].queryset.filter(
            group__account=self.context['request'].user.user.account)
        return fields

    user = serializers.PrimaryKeyRelatedField(label=_('user'), blank=True)
    permission = serializers.PrimaryKeyRelatedField(label=_('permission'))
    group = serializers.PrimaryKeyRelatedField(label=_('group'), blank=True)

    class Meta:
        model = AuthorRestriction