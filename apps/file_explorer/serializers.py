# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.publication.serializers import PublicationSerializer
from apps.file_explorer.models import File


class FileSerializer(PublicationSerializer):

    def get_fields(self):
        fields = super(FileSerializer, self).get_fields()
        queryset = fields['categories'].queryset
        fields['categories'].queryset = queryset.filter(account=self.context['request'].user.accountuser.account,
                                                        model_name='file')
        return fields

    class Meta(PublicationSerializer.Meta):
        model = File


class FileSerializerTest(FileSerializer):
    file = serializers.FileField(label=_('file'), blank=True)