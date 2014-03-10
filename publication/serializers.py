from rest_framework import serializers
from publication.models import Publication


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.Field(source='author.username')
    owner = serializers.Field(source='owner.username')
    is_published = serializers.HyperlinkedIdentityField(view_name='publication-is-published')
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta:
        model = Publication