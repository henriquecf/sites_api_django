from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import link
from rest_framework.response import Response
from category.models import Category
from category.serializers import CategorySerializer
from resource.views import ResourceViewSet


class CategoryViewSet(ResourceViewSet):
    serializer_class = CategorySerializer
    model = Category

    @link()
    def get_descendants(self, request, *agrs, **kwargs):
        """Returns the descendants of a category."""
        category = self.get_object()
        return Response(
            {'descendants': CategorySerializer(category.get_descendants(), context={'request': request},
                                               many=True).data})