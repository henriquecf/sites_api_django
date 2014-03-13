from rest_framework import serializers
from account.models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')

    class Meta:
        model = Account
        exclude = ['owner']