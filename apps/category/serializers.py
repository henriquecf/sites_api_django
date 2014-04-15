# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.category.models import Category
from apps.resource.serializers import ResourceSerializer


class CategorySerializer(ResourceSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(label=_('get descendants'),
                                                           view_name='category-get-descendants')
    is_leaf_node = serializers.Field(label=_('is leaf node'), source='category.is_leaf_node')

    class Meta(ResourceSerializer.Meta):
        model = Category