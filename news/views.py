from publication.views import OwnerViewSet
from .serializers import CategorySerializer
from .models import Category


class CategoryViewSet(OwnerViewSet):
    serializer_class = CategorySerializer
    model = Category