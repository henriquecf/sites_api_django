# -*- coding: utf-8 -*-
import django_filters
from apps.category.models import Category


class CategoryFilterSet(django_filters.FilterSet):

    class Meta:
        model = Category
        fields = ['model_name']