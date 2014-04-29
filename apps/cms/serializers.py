# -*- coding: utf-8 -*-

import ast

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from apps.publication.serializers import PublicationSerializer
from apps.cms.models import Page, Module, ModulePosition


class ModulePositionSerializer(PublicationSerializer):
    content = serializers.CharField(required=False, label=_('content'), widget=serializers.widgets.Textarea())

    class Meta(PublicationSerializer.Meta):
        model = ModulePosition


class ModuleSerializer(PublicationSerializer):
    model = serializers.PrimaryKeyRelatedField(source='model', label=_('model'),
                                               queryset=ContentType.objects.exclude(app_label__in=(
                                                   'admin', 'auth', 'contenttypes', 'oauth2_provider', 'sessions',
                                                   'sites', 'resource', 'cms', 'newsletter', 'category'
                                               )))
    content = serializers.CharField(required=False, label=_('content'), widget=serializers.widgets.Textarea())
    content_url = serializers.SerializerMethodField('get_content_url')
    pages = serializers.RelatedField(many=True)

    def get_content_url(self, obj):
        try:
            filter_dict = ast.literal_eval(obj.filters)
        except SyntaxError:
            filter_dict = {}
        try:
            get_query = urlencode(filter_dict)
        except AttributeError:
            get_query = urlencode(filter_dict)
        if get_query:
            url = 'http://{0}/{1}/?{2}'.format(self.context['request'].get_host(), obj.model.model.lower(), get_query)
        else:
            url = 'http://{0}/{1}/'.format(self.context['request'].get_host(), obj.model.model.lower())
        return url

    class Meta(PublicationSerializer.Meta):
        model = Module


class PageSerializer(PublicationSerializer):
    category = serializers.HyperlinkedRelatedField(view_name='category-detail', read_only=True, label=_('category'))
    content = serializers.CharField(required=False, label=_('content'), widget=serializers.widgets.Textarea())

    def get_fields(self):
        fields = super(PageSerializer, self).get_fields()
        fields['modules'] = ModuleSerializer(many=True, read_only=True, context=self.context)
        return fields

    class Meta(PublicationSerializer.Meta):
        model = Page