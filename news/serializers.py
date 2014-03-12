from rest_framework import serializers
from publication.serializers import OwnerSerializer
from .models import Category


class CategorySerializer(OwnerSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta:
        model = Category