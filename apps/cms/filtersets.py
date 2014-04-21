# -*- coding: utf-8 -*-
from apps.publication.filtersets import PublicationFilterSet
from apps.cms.models import Page


class PageFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Page