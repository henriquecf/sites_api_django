# -*- coding: utf-8 -*-
from apps.publication.filtersets import PublicationFilterSet
from apps.cms.models import Page, Module, ModulePosition


class PageFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Page


class ModuleFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Module


class ModulePositionFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = ModulePosition