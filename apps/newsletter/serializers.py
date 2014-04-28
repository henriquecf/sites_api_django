from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.resource.serializers import ResourceSerializer
from apps.newsletter.models import Subscription, Newsletter


class SubscriptionSerializer(ResourceSerializer):
    unsubscribe = serializers.HyperlinkedIdentityField(label=_('unsubscribe'), view_name='subscription-unsubscribe')
    submissions = serializers.RelatedField(label=_('submissions'), many=True, source='submissions')

    class Meta(ResourceSerializer.Meta):
        model = Subscription
        exclude = ['token']


class NewsletterSerializer(ResourceSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(label=_('send newsletter'),
                                                           view_name='newsletter-send-newsletter')
    submissions = serializers.RelatedField(label=_('submissions'), many=True, source='submissions')

    class Meta(ResourceSerializer.Meta):
        model = Newsletter