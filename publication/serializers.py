from rest_framework import serializers

from resource.serializers import ResourceSerializer
from publication.models import Publication, Category


class PublicationSerializer(ResourceSerializer):
    is_published = serializers.BooleanField(source='is_published', read_only=True)
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta(ResourceSerializer.Meta):
        model = Publication


class CategorySerializer(ResourceSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta(ResourceSerializer.Meta):
        model = Category