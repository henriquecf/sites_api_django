# -*- coding: utf-8 -*-
from apps.publication.filtersets import PublicationFilterSet
from apps.file_explorer.models import File


class FileFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = File