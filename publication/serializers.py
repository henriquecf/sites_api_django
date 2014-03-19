from rest_framework import serializers

from accounts.views import OwnerSerializer
from publication.models import Publication, Category


class PublicationSerializer(OwnerSerializer):
    author = serializers.Field(source='author.username')
    is_published = serializers.HyperlinkedIdentityField(view_name='publication-is-published')
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta(OwnerSerializer.Meta):
        model = Publication


class CategorySerializer(OwnerSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta(OwnerSerializer.Meta):
        model = Category