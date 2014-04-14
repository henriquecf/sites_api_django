# Create your views here.
from rest_framework.decorators import link
from rest_framework.response import Response

from apps.category.models import Category
from apps.category.filtersets import CategoryFilterSet
from apps.category.serializers import CategorySerializer
from apps.resource.views import ResourceViewSet


class CategoryViewSet(ResourceViewSet):
    serializer_class = CategorySerializer
    model = Category
    filter_class = CategoryFilterSet

    @link()
    def get_descendants(self, request, *agrs, **kwargs):
        """Returns the descendants of a category."""
        category = self.get_object()
        return Response(
            {'descendants': CategorySerializer(category.get_descendants(), context={'request': request, 'view': self},
                                               many=True).data})