from django.utils.text import slugify
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import link

from publication.models import Publication

from publication.serializers import PublicationSerializer
from accounts.views import OwnerViewSet
from .models import find_available_slug
from .filtersets import PublicationFilterSet


class PublicationBaseViewSet(OwnerViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Has some extra actions as publish, unpublish end check if is
    publisehd or not.
    """
    model = Publication
    serializer_class = PublicationSerializer
    filter_class = PublicationFilterSet
    search_fields = ('title', 'description')

    def pre_save(self, obj):
        super(PublicationBaseViewSet, self).pre_save(obj)
        # Makes the user who is posting the author of the publication
        obj.author = self.request.user
        # Creates a slug for the publication based on the title
        slug = slugify(obj.title)
        find_available_slug(self.model, obj, slug, slug)
        # Creates a publication_start_date for the publication in case it does not exists
        if not obj.publication_start_date:
            obj.publication_start_date = timezone.now()

    @link()
    def is_published(self):
        publication = self.get_object()
        return Response({'is_published': publication.is_published()})

    @link()
    def publish(self):
        publication = self.get_object()
        return Response({'is_published': publication.publish()})

    @link()
    def unpublish(self):
        publication = self.get_object()
        return Response({'is_published': publication.unpublish()})
