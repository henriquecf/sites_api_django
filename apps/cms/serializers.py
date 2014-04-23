# -*- coding: utf-8 -*-

import ast, urllib
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from apps.publication.serializers import PublicationSerializer
from apps.cms.models import Page, Module


class PageSerializer(PublicationSerializer):
    category = serializers.HyperlinkedRelatedField(view_name='category-detail', read_only=True)

    class Meta(PublicationSerializer.Meta):
        model = Page


class ModuleSerializer(PublicationSerializer):
    model = serializers.PrimaryKeyRelatedField(source='model')
    content_url = serializers.SerializerMethodField('get_content_url')

    def get_content_url(self, obj):
        try:
            filter_dict = ast.literal_eval(obj.filters)
        except SyntaxError:
            filter_dict = {}
        get_query = urllib.urlencode(filter_dict).decode()
        return 'http://{0}/{1}/?{2}'.format(self.context['request'].get_host(), obj.model.model.lower(), get_query)

    class Meta(PublicationSerializer.Meta):
        model = Module