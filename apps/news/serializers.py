from django.contrib.contenttypes.models import ContentType
from apps.publication.serializers import PublicationSerializer
from apps.news.models import News


class NewsSerializer(PublicationSerializer):

    def get_fields(self):
        fields = super(NewsSerializer, self).get_fields()
        file_content_type = ContentType.objects.get_for_model(News)
        fields['categories'].queryset = fields['categories'].queryset.filter(
            owner=self.context['request'].user.user.owner, model=file_content_type.id)
        return fields

    class Meta(PublicationSerializer.Meta):
        model = News