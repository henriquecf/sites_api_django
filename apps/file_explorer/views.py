from apps.publication.views import PublicationBaseViewSet
from apps.file_explorer.filtersets import FileFilterSet
from apps.file_explorer.models import File
from apps.file_explorer.serializers import FileSerializer, FileSerializerTest


class FileViewSet(PublicationBaseViewSet):
    filter_class = FileFilterSet
    model = File

    def get_serializer_class(self):
        if self.request.META.get('SERVER_NAME') == 'testserver':
            return FileSerializerTest
        else:
            return FileSerializer