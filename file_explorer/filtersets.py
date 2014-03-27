# -*- coding: utf-8 -*-
from publication.filtersets import PublicationFilterSet
from .models import File


class FileFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = File