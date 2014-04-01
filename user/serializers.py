# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AccountUser


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(view_name='account-detail', read_only=True)

    class Meta:
        model = AccountUser


class UserCreateChangeSerializer(serializers.HyperlinkedModelSerializer):
    """Must be called when a non safe method is being requested."""
    email = serializers.EmailField(required=True)
    accountuser = serializers.HyperlinkedRelatedField(view_name='accountuser-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'first_name', 'last_name', 'username', 'email', 'password', 'accountuser']


class UserSerializer(UserCreateChangeSerializer):
    """Must be called when a safe method is being requested."""

    class Meta(UserCreateChangeSerializer.Meta):
        fields = ['url', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'accountuser']