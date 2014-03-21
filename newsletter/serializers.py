from rest_framework import serializers
from publication.serializers import PublicationSerializer
from owner.serializers import OwnerSerializer
from .models import Subscription, Newsletter


class SubscriptionSerializer(OwnerSerializer):

    class Meta(OwnerSerializer.Meta):
        model = Subscription


class NewsletterSerializer(PublicationSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(view_name='newsletter-send-newsletter')

    class Meta(PublicationSerializer.Meta):
        model = Newsletter