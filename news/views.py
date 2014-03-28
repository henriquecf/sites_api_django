
from publication.views import PublicationBaseViewSet
from .serializers import NewsSerializer
from .models import News
from .filtersets import NewsFilterSet


class NewsViewSet(PublicationBaseViewSet):
    serializer_class = NewsSerializer
    model = News
    filter_class = NewsFilterSet
    # TODO find a way to get search fields from parent without having to rename them
    search_fields = ['title', 'description', 'content']
