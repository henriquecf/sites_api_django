from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.resource.serializers import ResourceSerializer
from apps.publication.models import Publication


class PublicationSerializer(ResourceSerializer):
    is_published = serializers.BooleanField(label=_('publication status'), source='is_published', read_only=True)
    publish = serializers.HyperlinkedIdentityField(label=_('publish'), view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(label=_('unpublish'), view_name='publication-unpublish')

    class Meta(ResourceSerializer.Meta):
        model = Publication


