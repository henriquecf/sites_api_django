from publication.views import PublicationBaseViewSet
from news.serializers import NewsSerializer
from news.models import News
from news.filtersets import NewsFilterSet


class NewsViewSet(PublicationBaseViewSet):
    serializer_class = NewsSerializer
    model = News
    filter_class = NewsFilterSet
    # TODO find a way to get search fields from parent without having to rename them
    search_fields = ['title', 'description', 'content']
