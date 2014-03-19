# -*- coding: utf-8 -*-
from publication.filtersets import PublicationFilterSet
from .models import News


class NewsFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = News