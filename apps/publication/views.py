from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.resource.views import ResourceViewSet
from apps.publication.serializers import PublicationSerializer, CustomHTMLSerializer
from apps.publication.models import find_available_slug, Publication, CustomHTML
from apps.publication.filtersets import PublicationFilterSet


class PublicationBaseViewSet(ResourceViewSet):
    """

    The fields title and description are defined as fields that can be searched.
    """
    model = Publication
    serializer_class = PublicationSerializer
    filter_class = PublicationFilterSet
    search_fields = ('title', 'description')

    def pre_save(self, obj):
        """Defines all actions needed before saving the object.

        Calls the actions from ResourceViewSet.
        Finds an available slug.
        Defines a publication start date, if it does not exist.
        """
        super(PublicationBaseViewSet, self).pre_save(obj)
        try:
            last_title = Publication.objects.get(id=obj.id).title
        except ObjectDoesNotExist:
            # Creates a slug for the publication based on the title
            slug = slugify(u'%s' % obj.title)
            find_available_slug(self.model, obj, slug, slug)
        else:
            try:
                title = self.request.DATA['title']
                if title != last_title:
                    # Creates a slug for the publication based on the title
                    slug = slugify(u'%s' % title)
                    find_available_slug(self.model, obj, slug, slug)
            except KeyError:
                pass
        # Creates a publication_start_date for the publication in case it does not exists
        if not obj.publication_start_date:
            obj.publication_start_date = timezone.now()

    @action()
    def publish(self, request, *args, **kwargs):
        """Link to publish the publication.

        Returns the state of the publication, if published or not.
        """
        publication = self.get_object()
        return Response({'is_published': publication.publish()})

    @action()
    def unpublish(self, request, *args, **kwargs):
        """Link to unpublish the publication.

        Returns the state of the publication, if published or not.
        """
        publication = self.get_object()
        return Response({'is_published': publication.unpublish()})


class PublicationViewSet(PublicationBaseViewSet):

    def create(self, request, *args, **kwargs):
        return Response(data={'detail': _('Method \'POST\' not allowed.')}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(data={'detail': _('Method \'PUT\' not allowed.')}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response(data={'detail': _('Method \'PATCH\' not allowed.')}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response(data={'detail': _('Method \'DELETE\' not allowed.')}, status=status.HTTP_400_BAD_REQUEST)


class CustomHTMLViewSet(PublicationBaseViewSet):
    model = CustomHTML
    serializer_class = CustomHTMLSerializer
    filter_class = None