from rest_framework import serializers
from publication.models import Publication
from .models import Account


class OwnerSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')

    class Meta:
        model = Account
        exclude = ['owner']


class PublicationSerializer(OwnerSerializer):
    author = serializers.Field(source='author.username')
    is_published = serializers.HyperlinkedIdentityField(view_name='publication-is-published')
    publish = serializers.HyperlinkedIdentityField(view_name='publication-publish')
    unpublish = serializers.HyperlinkedIdentityField(view_name='publication-unpublish')

    class Meta(OwnerSerializer.Meta):
        model = Publication