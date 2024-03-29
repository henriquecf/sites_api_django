# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group as AuthGroup, User as AuthUser, Permission
from rest_framework import serializers

from apps.resource.models import Resource, Group, User, AuthorRestriction


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission


class AuthUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = AuthUser
        exclude = ('is_superuser', 'is_staff')
        read_only_fields = ('date_joined', 'last_login', 'is_active', 'groups', 'user_permissions')
        write_only_fields = ('password',)


class NestedAuthUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'email')


class AuthGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthGroup
        fields = ('id', 'permissions')


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    author = NestedAuthUserSerializer(read_only=True)
    owner = NestedAuthUserSerializer(read_only=True)
    sites = serializers.PrimaryKeyRelatedField(many=True, required=False)

    def get_fields(self):
        fields = super(ResourceSerializer, self).get_fields()
        fields['sites'].queryset = fields['sites'].queryset.filter(
            site__owner=self.context['request'].user.user.owner)
        return fields

    class Meta:
        model = Resource


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
    assign_groups = serializers.HyperlinkedIdentityField(label=_('assign groups'), view_name='user-assign-groups')
    unassign_groups = serializers.HyperlinkedIdentityField(label=_('unassign groups'), view_name='user-unassign-groups')
    assign_permissions = serializers.HyperlinkedIdentityField(label=_('assign permissions'),
                                                              view_name='user-assign-permissions')
    unassign_permissions = serializers.HyperlinkedIdentityField(label=_('unassign permissions'),
                                                                view_name='user-unassign-permissions')

    class Meta(ResourceSerializer.Meta):
        model = User


class AuthorRestrictionSerializer(ResourceSerializer):
    user = serializers.PrimaryKeyRelatedField(label=_('user'), blank=True)
    permission = serializers.PrimaryKeyRelatedField(label=_('permission'))
    group = serializers.PrimaryKeyRelatedField(label=_('group'), blank=True)

    def get_fields(self):
        fields = super(AuthorRestrictionSerializer, self).get_fields()
        fields['user'].queryset = fields['user'].queryset.filter(
            user__owner=self.context['request'].user.user.owner)
        fields['group'].queryset = fields['group'].queryset.filter(
            group__owner=self.context['request'].user.user.owner)
        queryset = fields['permission'].queryset
        queryset = queryset.exclude(content_type__app_label__in=['admin', 'auth', 'contenttypes', 'oauth2_provider',
                                                                 'sessions', 'sites'])
        fields['permission'].queryset = queryset
        return fields

    class Meta(ResourceSerializer.Meta):
        model = AuthorRestriction