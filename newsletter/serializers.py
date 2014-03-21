from rest_framework import serializers
from publication.serializers import PublicationSerializer
from accounts.serializers import OwnerSerializer
from .models import Subscriptions, Newsletter


class SubscriptionsSerializer(OwnerSerializer):

    class Meta(OwnerSerializer.Meta):
        model = Subscriptions


class NewsletterSerializer(PublicationSerializer):
    send_newsletter = serializers.HyperlinkedIdentityField(view_name='newsletter-send-newsletter')

    class Meta(PublicationSerializer.Meta):
        model = Newsletter