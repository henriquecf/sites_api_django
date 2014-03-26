from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedIdentityField(view_name='user-list')

    class Meta:
        model = Account