from rest_framework.decorators import link
from rest_framework.response import Response
from account.views import AccountBaseViewSet
from publication.views import PublicationBaseViewSet
from .serializers import CategorySerializer, NewsSerializer
from .models import Category, News


class CategoryBaseViewSet(AccountBaseViewSet):
    serializer_class = CategorySerializer
    model = Category

    @link()
    def get_descendants(self, request, *agrs, **kwargs):
        category = self.get_object()
        return Response({'descendants': CategorySerializer(category.get_descendants(), context={'request': request}).data})


class NewsViewSet(PublicationBaseViewSet):
    serializer_class = NewsSerializer
    model = News
