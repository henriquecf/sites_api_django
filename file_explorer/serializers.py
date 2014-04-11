# -*- coding: utf-8 -*-
from rest_framework import serializers
from publication.serializers import PublicationSerializer
from file_explorer.models import File


class FileSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = File


class FileSerializerTest(FileSerializer):
    file = serializers.FileField(blank=True)