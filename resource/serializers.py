# -*- coding: utf-8 -*-
from rest_framework import serializers

from account.models import Account
from resource.models import AccountSite


class ResourceSerializer(serializers.HyperlinkedModelSerializer):

    def get_fields(self):
        fields = super(ResourceSerializer, self).get_fields()
        fields['sites'].queryset = AccountSite.objects.filter(
            account=self.context['request'].user.accountuser.account)
        return fields

    class Meta:
        model = Account
        read_only_fields = ('creator', 'account')


class AccountSiteSerializer(serializers.HyperlinkedModelSerializer):
    site = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AccountSite