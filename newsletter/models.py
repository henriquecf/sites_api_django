import random
from django.db import models
from django.core.mail import EmailMultiAlternatives
from owner.models import Owner


class Subscription(Owner):
    """
    This class holds the newsletter subscribers
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)
    token = models.CharField(max_length=30, editable=False)
    active = models.BooleanField(default=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        equal_subscriptions = Subscription.objects.filter(owner_id=self.owner.id, email=self.email)
        active = self.active
        for subscription in equal_subscriptions:
            if not subscription == self:
                active = subscription.active
                subscription.delete()
        self.token = random.randint(948284593853, 958272838472748584737484748234)
        self.active = active
        return super(Subscription, self).save()

    def __str__(self):
        return self.name


class Newsletter(Owner):
    """
    This model implements newsletter as a publication.
    """
    subject = models.CharField(max_length=200)
    content = models.TextField()

    def send_newsletter(self, user):
        subscriptions = Subscription.objects.filter(owner=user)
        for subscription in subscriptions:
            message = EmailMultiAlternatives(self.title,
                                             self.content,
                                             'localhost',
                                             subscription.email)
            message.send()
        return True


class Submission(Owner):
    """
    This class holds the submission of a newsletter to a subscriber
    """
    subscription = models.ForeignKey(Subscription)
    newsletter = models.ForeignKey(Newsletter)

    def send_newsletter(self, user):
        message = EmailMultiAlternatives(self.title,
                                         self.newsletter.content,
                                         'localhost',
                                         self.subscription.email)
        message.send()
        return True