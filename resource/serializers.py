# -*- coding: utf-8 -*-
from rest_framework import serializers

from accounts.models import Account


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.Field(source='creator.username')

    class Meta:
        model = Account
        exclude = ['account', 'creator']