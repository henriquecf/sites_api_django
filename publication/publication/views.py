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
    Has some extra actions as publish, unpublish end check if is
    publisehd or not.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def pre_save(self, obj):
        obj.author = self.request.user

    @link()
    def is_published(self, request, *args, **kwargs):
        publication = self.get_object()
        return Response(publication.is_published())


    @link()
    def publish(self, request, *args, **kwargs):
        publication = self.get_object()
        return Response(publication.publish())

    @link()
    def unpublish(self, request, *args, **kwargs):
        publication = self.get_object()
        return Response(publication.unpublish())
