# -*- coding: utf-8 -*-
import django_filters
from .models import Publication


class PublicationFilterSet(django_filters.FilterSet):

    class Meta:
        model = Publication
        fields = []