# -*- coding: utf-8 -*-
from rest_framework import serializers

from accounts.models import Account


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(view_name='account-detail', read_only=True)

    class Meta:
        model = Account
        exclude = ['creation_date', 'last_modification_date']