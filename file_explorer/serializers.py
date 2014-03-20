# -*- coding: utf-8 -*-
from publication.serializers import PublicationSerializer
from .models import File


class FileSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = File