from django.contrib.auth.models import User
from rest_framework import serializers
from account.models import AccountUser, Account, AccountGroup, FilterRestriction


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)

    class Meta:
        model = Account


class AccountUserSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(view_name='account-detail', read_only=True)

    class Meta:
        model = AccountUser


class UserCreateChangeSerializer(serializers.HyperlinkedModelSerializer):
    """Must be called when a non safe method is being requested."""
    email = serializers.EmailField(required=True)
    accountuser = serializers.HyperlinkedRelatedField(view_name='accountuser-detail', read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        exclude = ['is_superuser']


class UserSerializer(UserCreateChangeSerializer):
    """Must be called when a safe method is being requested."""

    class Meta(UserCreateChangeSerializer.Meta):
        exclude = ['is_superuser', 'password']


class AccountGroupSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(view_name='account-detail', read_only=True)
    group = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)

    class Meta:
        model = AccountGroup


class FilterRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    accountuser = serializers.PrimaryKeyRelatedField(blank=True)
    permission = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = FilterRestriction