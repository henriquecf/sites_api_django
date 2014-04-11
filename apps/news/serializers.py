from apps.publication.serializers import PublicationSerializer
from apps.news.models import News


class NewsSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = News