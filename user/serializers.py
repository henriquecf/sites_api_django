# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AccountUser


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedIdentityField(view_name='user-list')
    account = serializers.HyperlinkedIdentityField(view_name='account-list')

    class Meta:
        model = AccountUser


class UserCreateChangeSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['url', 'first_name', 'last_name', 'username', 'email', 'password']


class UserSerializer(UserCreateChangeSerializer):

    class Meta(UserCreateChangeSerializer.Meta):
        fields = ['url', 'username', 'email', 'first_name', 'last_name']