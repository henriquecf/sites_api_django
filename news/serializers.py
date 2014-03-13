from rest_framework import serializers
from publication.serializers import OwnerSerializer, PublicationSerializer
from .models import Category, News


class CategorySerializer(OwnerSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta(OwnerSerializer.Meta):
        model = Category


class NewsSerializer(PublicationSerializer):
    image = serializers.ImageField(source='news.image', required=False)

    class Meta(PublicationSerializer.Meta):
        model = News