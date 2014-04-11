# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.publication.serializers import PublicationSerializer
from apps.file_explorer.models import File


class FileSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = File


class FileSerializerTest(FileSerializer):
    file = serializers.FileField(blank=True)