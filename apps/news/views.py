from apps.publication.views import PublicationBaseViewSet
from apps.news.serializers import NewsSerializer
from apps.news.models import News
from apps.news.filtersets import NewsFilterSet


class NewsViewSet(PublicationBaseViewSet):
    serializer_class = NewsSerializer
    model = News
    filter_class = NewsFilterSet
    # TODO find a way to get search fields from parent without having to rename them
    search_fields = ['title', 'description', 'content']
