# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from apps.publication.serializers import PublicationSerializer
from apps.cms.models import Page, Module


class PageSerializer(PublicationSerializer):
    category = serializers.HyperlinkedRelatedField(view_name='category-detail', read_only=True)

    class Meta(PublicationSerializer.Meta):
        model = Page


class ModuleSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = Module