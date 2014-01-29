from rest_framework import viewsets
from publication.models import Publication
from publication.serializers import PublicationSerializer

class PublicationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer