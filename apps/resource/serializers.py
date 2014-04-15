# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from apps.resource.models import AccountSite, Resource


class ResourceSerializer(serializers.HyperlinkedModelSerializer):

    def get_fields(self):
        fields = super(ResourceSerializer, self).get_fields()
        fields['sites'].queryset = fields['sites'].queryset.filter(
            account=self.context['request'].user.accountuser.account)
        return fields

    class Meta:
        model = Resource
        read_only_fields = ('author', 'account')


class AccountSiteSerializer(serializers.HyperlinkedModelSerializer):
    site = serializers.PrimaryKeyRelatedField(label=_('site'), read_only=True)

    class Meta:
        model = AccountSite