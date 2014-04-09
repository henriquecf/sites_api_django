import random
from django.db import models
from django.core.mail import EmailMultiAlternatives
from resource.models import Resource


class Subscription(Resource):
    """Holds information about the newsletter subscribers.

    It holds the name and email, obligatory fields to create a subscription.
    Besides these fields, it automatically generates a token to deactivate
    and put subscription status in a boolean field.
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200, unique=True)
    token = models.CharField(max_length=30, editable=False)
    active = models.BooleanField(default=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.token = random.randint(948284593853, 958272838472748584737484748234)
        return super(Subscription, self).save()

    def __str__(self):
        return self.name


class Newsletter(Resource):
    """
    This model implements newsletter as a publication.
    """
    subject = models.CharField(max_length=200)
    content = models.TextField()

    def send_newsletter(self, account):
        subscriptions = Subscription.objects.filter(account=account)
        for subscription in subscriptions:
            submission = Submission.objects.create(account=self.account,
                                                   creator=self.account.owner,
                                                   newsletter=self,
                                                   subscription=subscription)
            submission.send_newsletter()
        return True


class Submission(Resource):
    """Holds the submission information.

    This model is related with a newsletter object and a subscription object.
    """
    subscription = models.ForeignKey(Subscription)
    newsletter = models.ForeignKey(Newsletter)

    def send_newsletter(self):
        """Sends a newsletter to the subscription in the subscription field.

        Keyword arguments:

        user -- Not used in this context. Held for compatibility.
        """
        message = EmailMultiAlternatives(self.newsletter.subject,
                                         self.newsletter.content,
                                         'localhost',
                                         [self.subscription.email])
        status = message.send()
        print(message.get_connection().status)
        return True

    class Meta:
        unique_together = ('subscription', 'newsletter')