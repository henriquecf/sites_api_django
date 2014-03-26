# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import AccountUser


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AccountUser
        fields = ['url', 'user', 'account']