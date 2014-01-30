from rest_framework import viewsets, permissions
from publication.models import Publication
from publication.serializers import PublicationSerializer

class PublicationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def pre_save(self, obj):
        obj.author = self.request.user