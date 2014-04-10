# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from rest_framework import serializers

from account.models import Account


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    account = serializers.HyperlinkedRelatedField(view_name='account-detail', read_only=True)

    class Meta:
        model = Account


class SiteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Site