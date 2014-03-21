# -*- coding: utf-8 -*-
from rest_framework import serializers

from accounts.models import Account


class OwnerSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')

    class Meta:
        model = Account
        exclude = ['owner']