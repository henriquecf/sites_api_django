# -*- coding: utf-8 -*-

from apps.publication.views import PublicationBaseViewSet
from apps.cms.serializers import PageSerializer
from apps.cms.filtersets import PageFilterSet
from apps.cms.models import Page


class PageViewSet(PublicationBaseViewSet):
    serializer_class = PageSerializer
    model = Page
    filter_class = PageFilterSet
    search_fields = ['title', 'description']

    def post_save(self, obj, created=False):
        super(PageViewSet, self).post_save(obj, created=created)
        obj.category.sites = obj.sites.all()
        obj.save()
