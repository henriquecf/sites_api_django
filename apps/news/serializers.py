from rest_framework import serializers

from apps.publication.serializers import PublicationSerializer
from apps.news.models import News


class NewsSerializer(PublicationSerializer):
    image = serializers.ImageField(source='news.image', required=False)

    class Meta(PublicationSerializer.Meta):
        model = News