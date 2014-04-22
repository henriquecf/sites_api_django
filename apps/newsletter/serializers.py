from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.resource.serializers import ResourceSerializer
from apps.newsletter.models import Subscription, Newsletter, Submission


class SubscriptionSerializer(ResourceSerializer):
    unsubscribe = serializers.HyperlinkedIdentityField(label=_('unsubscribe'), view_name='subscription-unsubscribe')

    class Meta(ResourceSerializer.Meta):
        model = Subscription


class SubmissionSerializer(ResourceSerializer):
    newsletter = serializers.RelatedField(label=_('newsletter'), read_only=True)
    subscription = serializers.RelatedField(label=_('subscription'), read_only=True)

    class Meta(ResourceSerializer.Meta):
        model = Submission


class NewsletterSerializer(ResourceSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(label=_('send newsletter'),
                                                           view_name='newsletter-send-newsletter')
    submissions = serializers.RelatedField(label=_('submissions'), many=True, source='submissions')

    class Meta(ResourceSerializer.Meta):
        model = Newsletter