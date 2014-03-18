from rest_framework import serializers

from accounts.views import OwnerSerializer
from publication.models import Publication


class PublicationSerializer(OwnerSerializer):
    author = serializers.Field(source='author.username')
    is_published = serializers.HyperlinkedIdentityField(view_name='publication-is-published')
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta(OwnerSerializer.Meta):
        model = Publication