from publication.serializers import OwnerSerializer
from .models import Category


# TODO Put parent field here when parent field become implemented in model
class CategorySerializer(OwnerSerializer):

    class Meta:
        model = Category