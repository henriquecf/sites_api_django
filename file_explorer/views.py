from publication.views import PublicationBaseViewSet
from .filtersets import FileFilterSet
from .models import File
from .serializers import FileSerializer, FileSerializerTest


class FileViewSet(PublicationBaseViewSet):
    filter_class = FileFilterSet
    model = File

    def get_serializer_class(self):
        if self.request.META.get('SERVER_NAME') == 'testserver':
            return FileSerializerTest
        else:
            return FileSerializer