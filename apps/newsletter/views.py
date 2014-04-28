from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.resource.views import ResourceViewSet
from apps.newsletter.serializers import SubscriptionSerializer, NewsletterSerializer
from apps.newsletter.models import Subscription, Newsletter
from apps.newsletter.filtersets import NewsletterFilterSet


class SubscriptionViewSet(ResourceViewSet):
    serializer_class = SubscriptionSerializer
    model = Subscription

    def create(self, request, *args, **kwargs):
        try:
            subscription = Subscription.objects.get(email=request.DATA['email'],
                                                    owner=request.user.user.owner)
        except Subscription.DoesNotExist:
            return super(SubscriptionViewSet, self).create(request, *args, **kwargs)
        else:
            subscription.is_active = True
            subscription.save()
            serialized_data = SubscriptionSerializer(subscription, context={'request': request})
            return Response(data=serialized_data.data, status=201)

    @action()
    def unsubscribe(self, request, *args, **kwargs):
        """Verify token and subscriber to deactivate a subscritpion.

        If token does not match for the user, a 400 status code is returned.
        """
        subscription = self.get_object()
        try:
            token = request.DATA['token']
        except KeyError:
            return Response(status=400, data={'detail': _('You can not unsubscribe without a valid token.')})
        if subscription.token == token:
            subscription.is_active = False
            subscription.save()
            return Response(status=200, data={'detail': _('You was successfully unsubscribed.')})
        else:
            return Response(status=400, data={'detail': _('You can not unsubscribe without a valid token.')})


class NewsletterViewSet(ResourceViewSet):
    serializer_class = NewsletterSerializer
    model = Newsletter
    filter_class = NewsletterFilterSet

    @action()
    def send_newsletter(self, request, *args, **kwargs):
        """Send the newsletter calling the model function."""
        newsletter = self.get_object()
        status = newsletter.send_newsletter(owner=request.user.user.owner)
        data = {
            'submissions': status,
        }
        return Response(status=200, data=data)