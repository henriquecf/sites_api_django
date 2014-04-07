# -*- coding: utf-8 -*-
from rest_framework import serializers
from category.models import Category
from resource.serializers import ResourceSerializer


class CategorySerializer(ResourceSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta(ResourceSerializer.Meta):
        model = Category