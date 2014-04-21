# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from apps.publication.serializers import PublicationSerializer
from apps.cms.models import Page


class PageSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = Page