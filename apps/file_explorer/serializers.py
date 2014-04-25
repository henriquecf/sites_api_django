# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from apps.publication.serializers import PublicationSerializer
from apps.file_explorer.models import File


class FileSerializer(PublicationSerializer):
    content = serializers.CharField(required=False, label=_('content'), widget=serializers.widgets.Textarea())

    def get_fields(self):
        fields = super(FileSerializer, self).get_fields()
        file_content_type = ContentType.objects.get_for_model(File)
        fields['categories'].queryset = fields['categories'].queryset.filter(
            owner=self.context['request'].user.user.owner, model=file_content_type.id)
        return fields

    class Meta(PublicationSerializer.Meta):
        model = File


class FileSerializerTest(FileSerializer):
    file = serializers.FileField(label=_('file'), blank=True)