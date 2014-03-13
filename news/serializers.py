from rest_framework import serializers
from account.views import AccountSerializer
from publication.serializers import PublicationSerializer
from .models import Category, News


class CategorySerializer(AccountSerializer):
    get_descendants = serializers.HyperlinkedIdentityField(view_name='category-get-descendants')
    is_leaf_node = serializers.Field(source='category.is_leaf_node')

    class Meta(AccountSerializer.Meta):
        model = Category


class NewsSerializer(PublicationSerializer):
    image = serializers.ImageField(source='news.image', required=False)

    class Meta(PublicationSerializer.Meta):
        model = News