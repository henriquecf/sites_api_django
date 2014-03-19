from publication.views import PublicationBaseViewSet
from accounts.views import OwnerViewSet
from .serializers import SubscriptionsSerializer, NewsletterSerializer
from .models import Subscriptions, Newsletter
from .filtersets import NewsletterFilterSet


class SubscriptionsViewSet(OwnerViewSet):
    serializer_class = SubscriptionsSerializer
    model = Subscriptions


class NewsletterViewSet(PublicationBaseViewSet):
    serializer_class = NewsletterSerializer
    model = Newsletter
    filter_class = NewsletterFilterSet