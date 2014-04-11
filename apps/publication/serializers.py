from rest_framework import serializers

from apps.resource.serializers import ResourceSerializer
from apps.publication.models import Publication


class PublicationSerializer(ResourceSerializer):
    is_published = serializers.BooleanField(source='is_published', read_only=True)
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta(ResourceSerializer.Meta):
        model = Publication


