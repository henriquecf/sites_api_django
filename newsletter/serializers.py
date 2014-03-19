from rest_framework import serializers
from publication.serializers import PublicationSerializer
from accounts.serializers import OwnerSerializer
from .models import Subscriptions, Newsletter


class SubscriptionsSerializer(OwnerSerializer):

    class Meta(OwnerSerializer.Meta):
        model = Subscriptions


class NewsletterSerializer(PublicationSerializer):

    class Meta(PublicationSerializer.Meta):
        model = Newsletter