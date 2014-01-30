from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import link
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

    @link()
    def is_published(self, request, *args, **kwargs):
        publication = self.get_object()
        if publication.publication_end_date:
            if publication.publication_start_date > timezone.now() or publication.publication_end_date < timezone.now():
                return Response(False)
            else:
                return Response(True)
        elif publication.publication_start_date > timezone.now():
            return Response(False)
        else:
            return Response(True)