# -*- coding: utf-8 -*-

from apps.publication.views import PublicationBaseViewSet
from apps.cms.serializers import PageSerializer, ModuleSerializer
from apps.cms.filtersets import PageFilterSet, ModuleFilterSet
from apps.cms.models import Page, Module


class PageViewSet(PublicationBaseViewSet):
    serializer_class = PageSerializer
    model = Page
    filter_class = PageFilterSet
    search_fields = ['title', 'description']

    def post_save(self, obj, created=False):
        super(PageViewSet, self).post_save(obj, created=created)
        obj.category.sites = obj.sites.all()
        obj.save()


class ModuleViewSet(PublicationBaseViewSet):
    serializer_class = ModuleSerializer
    model = Module
    filter_class = ModuleFilterSet
    search_fields = ['title', 'description']