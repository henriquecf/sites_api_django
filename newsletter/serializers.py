from rest_framework import serializers
from resource.serializers import ResourceSerializer
from .models import Subscription, Newsletter, Submission


class SubscriptionSerializer(ResourceSerializer):
    unsubscribe = serializers.HyperlinkedIdentityField(view_name='subscription-unsubscribe')

    class Meta(ResourceSerializer.Meta):
        model = Subscription


class NewsletterSerializer(ResourceSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(view_name='newsletter-send-newsletter')

    class Meta(ResourceSerializer.Meta):
        model = Newsletter


class SubmissionSerializer(ResourceSerializer):
    newsletter = serializers.HyperlinkedRelatedField(view_name='newsletter-detail', read_only=True)
    subscription = serializers.HyperlinkedRelatedField(view_name='subscription-detail', read_only=True)

    class Meta(ResourceSerializer.Meta):
        model = Submission