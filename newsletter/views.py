
from rest_framework.decorators import link
from rest_framework.response import Response
from publication.views import PublicationBaseViewSet
from owner.views import OwnerViewSet
from .serializers import SubscriptionSerializer, NewsletterSerializer
from .models import Subscription, Newsletter
from .filtersets import NewsletterFilterSet


class SubscriptionViewSet(OwnerViewSet):
    serializer_class = SubscriptionSerializer
    model = Subscription


class NewsletterViewSet(PublicationBaseViewSet):
    serializer_class = NewsletterSerializer
    model = Newsletter
    filter_class = NewsletterFilterSet

    @link()
    def send_newsletter(self, request, *args, **kwargs):
        newsletter = self.get_object()
        status = newsletter.send_newsletter()
        if status:
            return Response(status=200)
