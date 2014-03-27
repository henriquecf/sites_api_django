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

    class Meta(ResourceSerializer.Meta):
        model = Submission