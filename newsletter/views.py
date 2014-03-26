
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import link, action
from rest_framework.response import Response
from resource.views import ResourceViewSet
from .serializers import SubscriptionSerializer, NewsletterSerializer, SubmissionSerializer
from .models import Subscription, Newsletter, Submission
from .filtersets import NewsletterFilterSet


class SubscriptionViewSet(ResourceViewSet):
    serializer_class = SubscriptionSerializer
    model = Subscription

    @link()
    def unsubscribe(self, request, *args, **kwargs):
        subscription = self.get_object()
        if subscription.token == request.GET['token']:
            subscription.active = False
            subscription.save()
            return Response(status=202)
        else:
            return Response(status=401)


class NewsletterViewSet(ResourceViewSet):
    serializer_class = NewsletterSerializer
    model = Newsletter
    filter_class = NewsletterFilterSet

    @link()
    def send_newsletter(self, request, *args, **kwargs):
        newsletter = self.get_object()
        status = newsletter.send_newsletter()
        if status:
            return Response(status=200)


class SubmissionViewSet(ResourceViewSet):
    serializer_class = SubmissionSerializer
    model = Submission