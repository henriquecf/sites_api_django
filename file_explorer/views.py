from publication.views import PublicationBaseViewSet
from .filtersets import FileFilterSet
from .models import File
from .serializers import FileSerializer


class FileViewSet(PublicationBaseViewSet):
    filter_class = FileFilterSet
    model = File
    serializer_class = FileSerializer
