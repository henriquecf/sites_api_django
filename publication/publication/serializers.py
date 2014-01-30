from rest_framework import serializers
from publication.models import Publication


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.Field(source='author.username')

    class Meta:
        model = Publication
        #fields = ('title', 'description', 'slug', 'publication_start_date', 'publication_end_date')