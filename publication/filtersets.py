# -*- coding: utf-8 -*-
import django_filters
from .models import Publication


class PublicationFilterSet(django_filters.FilterSet):
    author = django_filters.CharFilter(name='author__username')

    class Meta:
        model = Publication
        fields = ['author']