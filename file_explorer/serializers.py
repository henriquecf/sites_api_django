# -*- coding: utf-8 -*-
from rest_framework import serializers
from publication.serializers import PublicationSerializer
from file_explorer.models import File


class FileSerializer(PublicationSerializer):
    file = serializers.FileField(blank=True)

    class Meta(PublicationSerializer.Meta):
        model = File