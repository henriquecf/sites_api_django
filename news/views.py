from rest_framework.decorators import link
from rest_framework.response import Response
from accounts.views import OwnerViewSet
from publication.views import PublicationBaseViewSet
from .serializers import CategorySerializer, NewsSerializer
from .models import Category, News
from .filtersets import NewsFilterSet


class CategoryBaseViewSet(OwnerViewSet):
    serializer_class = CategorySerializer
    model = Category

    @link()
    def get_descendants(self, request, *agrs, **kwargs):
        category = self.get_object()
        return Response(
            {'descendants': CategorySerializer(category.get_descendants(), context={'request': request}).data})


class NewsViewSet(PublicationBaseViewSet):
    serializer_class = NewsSerializer
    model = News
    filter_class = NewsFilterSet
    # TODO find a way to get search fields from parent without having to rename them
    search_fields = ['title', 'description', 'content']
