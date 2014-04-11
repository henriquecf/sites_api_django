# -*- coding: utf-8 -*-
import django_filters

from apps.publication.filtersets import PublicationFilterSet
from apps.news.models import News


class NewsFilterSet(PublicationFilterSet):
    categories = django_filters.CharFilter(name='categories__name')

    class Meta(PublicationFilterSet.Meta):
        model = News
        fields = ['categories']