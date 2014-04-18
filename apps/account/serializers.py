# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.account.models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(label=_('owner'), view_name='user-detail', read_only=True)

    class Meta:
        model = Account


class UserSerializer(serializers.HyperlinkedModelSerializer):
    #def get_fields(self):
    #    fields = super(UserSerializer, self).get_fields()
    #    fields['groups'].queryset = fields['groups'].queryset.filter(
    #        group__account=self.context['request'].user.accountuser.account)
    #    return fields

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        exclude = ['is_superuser']
        read_only_fields = ('date_joined', 'last_login', 'is_active')
        write_only_fields = ('password',)


class RestrictedOwnerUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('date_joined', 'last_login', 'is_active', 'is_staff', 'user_permissions', 'groups')


