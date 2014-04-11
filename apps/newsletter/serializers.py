from rest_framework import serializers

from apps.resource.serializers import ResourceSerializer
from apps.newsletter.models import Subscription, Newsletter, Submission


class SubscriptionSerializer(ResourceSerializer):
    unsubscribe = serializers.HyperlinkedIdentityField(view_name='subscription-unsubscribe')

    class Meta(ResourceSerializer.Meta):
        model = Subscription


class SubmissionSerializer(ResourceSerializer):
    newsletter = serializers.RelatedField(read_only=True)
    subscription = serializers.RelatedField(read_only=True)

    class Meta(ResourceSerializer.Meta):
        model = Submission


class NewsletterSerializer(ResourceSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(view_name='newsletter-send-newsletter')
    submissions = serializers.RelatedField(many=True, source='submissions')

    class Meta(ResourceSerializer.Meta):
        model = Newsletter