from apps.publication.serializers import PublicationSerializer
from apps.news.models import News


class NewsSerializer(PublicationSerializer):
    def get_fields(self):
        fields = super(NewsSerializer, self).get_fields()
        fields['categories'].queryset = fields['categories'].queryset.filter(
            account=self.context['request'].user.user.account, model_name='news')
        return fields

    class Meta(PublicationSerializer.Meta):
        model = News