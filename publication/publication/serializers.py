from rest_framework import serializers
from publication.models import Publication


class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        fields = ('title', 'description', 'slug', 'publication_start_date', 'publication_end_date')