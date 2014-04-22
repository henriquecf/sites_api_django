# -*- coding: utf-8 -*-
from apps.publication.filtersets import PublicationFilterSet
from apps.cms.models import Page, Module


class PageFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Page


class ModuleFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Module