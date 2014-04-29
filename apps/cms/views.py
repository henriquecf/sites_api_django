# -*- coding: utf-8 -*-

from rest_framework.decorators import link
from apps.publication.views import PublicationBaseViewSet
from apps.cms.serializers import PageSerializer, ModuleSerializer, ModulePositionSerializer
from apps.cms.filtersets import PageFilterSet, ModuleFilterSet, ModulePositionFilterSet
from apps.cms.models import Page, Module, ModulePosition


class PageViewSet(PublicationBaseViewSet):
    serializer_class = PageSerializer
    model = Page
    filter_class = PageFilterSet

    def post_save(self, obj, created=False):
        super(PageViewSet, self).post_save(obj, created=created)
        obj.category.sites = obj.sites.all()
        obj.save()


class ModuleViewSet(PublicationBaseViewSet):
    serializer_class = ModuleSerializer
    model = Module
    filter_class = ModuleFilterSet


class ModulePositionViewSet(PublicationBaseViewSet):
    serializer_class = ModulePositionSerializer
    model = ModulePosition
    filter_class = ModulePositionFilterSet