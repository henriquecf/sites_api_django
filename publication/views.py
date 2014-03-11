from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import link
from publication.models import Publication, Owner
from publication.serializers import PublicationSerializer, OwnerSerializer


class OwnerViewSet(viewsets.ModelViewSet):
    serializer_class = OwnerSerializer
    model = Owner

    def pre_save(self, obj):
        obj.owner = self.request.user

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class PublicationViewSet(OwnerViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Has some extra actions as publish, unpublish end check if is
    publisehd or not.
    """
    model = Publication
    serializer_class = PublicationSerializer


    def pre_save(self, obj):
        super(PublicationViewSet, self).pre_save(obj)
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
