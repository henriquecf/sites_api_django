
from rest_framework.decorators import link
from rest_framework.response import Response
from owner.views import OwnerViewSet
from .serializers import SubscriptionSerializer, NewsletterSerializer, SubmissionSerializer
from .models import Subscription, Newsletter, Submission
from .filtersets import NewsletterFilterSet


class SubscriptionViewSet(OwnerViewSet):
    serializer_class = SubscriptionSerializer
    model = Subscription


class NewsletterViewSet(OwnerViewSet):
    serializer_class = NewsletterSerializer
    model = Newsletter
    filter_class = NewsletterFilterSet

    @link()
    def send_newsletter(self, request, *args, **kwargs):
        newsletter = self.get_object()
        status = newsletter.send_newsletter()
        if status:
            return Response(status=200)


class SubmissionViewSet(OwnerViewSet):
    serializer_class = SubmissionSerializer
    model = Submission