from rest_framework import serializers
from owner.serializers import OwnerSerializer
from .models import Subscription, Newsletter, Submission


class SubscriptionSerializer(OwnerSerializer):
    unsubscribe = serializers.HyperlinkedIdentityField(view_name='subscription-unsubscribe')

    class Meta(OwnerSerializer.Meta):
        model = Subscription


class NewsletterSerializer(OwnerSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(view_name='newsletter-send-newsletter')

    class Meta(OwnerSerializer.Meta):
        model = Newsletter

class SubmissionSerializer(OwnerSerializer):

    class Meta(OwnerSerializer.Meta):
        model = Submission