import random
import string
from django.db import models
from django.db.utils import IntegrityError
from django.core.mail import EmailMultiAlternatives

from apps.resource.models import Resource


class Subscription(Resource):
    """Holds information about the newsletter subscribers.

    It holds the name and email, obligatory fields to create a subscription.
    Besides these fields, it automatically generates a token to deactivate
    and put subscription status in a boolean field.
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)
    token = models.CharField(max_length=30, editable=False)
    active = models.BooleanField(default=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.token = ''.join(random.sample(string.ascii_letters, 15))
        return super(Subscription, self).save()

    def __str__(self):
        return self.email


class Newsletter(Resource):
    """
    This model implements newsletter as a publication.
    """
    subject = models.CharField(max_length=200)
    content = models.TextField()

    def send_newsletter(self, account):
        subscriptions = Subscription.objects.filter(account=account)
        resent = Submission.objects.filter(newsletter=self, status='failed')
        for subscription in subscriptions:
            try:
                Submission.objects.create(account=self.account,
                                          creator=self.account.owner,
                                          newsletter=self,
                                          subscription=subscription,)
            except IntegrityError:
                pass
        new = Submission.objects.filter(newsletter=self, status='new')
        for submission in new:
            submission.send_newsletter()
        for submission in resent:
            submission.send_newsletter()
        status = dict(new=new.count(),
                      successful=Submission.objects.filter(newsletter=self, status='sent').count(),
                      failed=Submission.objects.filter(newsletter=self, status='failed').count(),
                      resubmissions=resent.count())
        return status


class Submission(Resource):
    """Holds the submission information.

    This model is related with a newsletter object and a subscription object.
    """
    subscription = models.ForeignKey(Subscription, related_name='submissions')
    newsletter = models.ForeignKey(Newsletter, related_name='submissions')
    status = models.CharField(max_length='10', default='new')

    def send_newsletter(self):
        """Sends a newsletter to the subscription in the subscription field.

        Keyword arguments:

        user -- Not used in this context. Held for compatibility.
        """
        if not self.status == 'sent':
            message = EmailMultiAlternatives(self.newsletter.subject,
                                             self.newsletter.content,
                                             'localhost',
                                             [self.subscription.email])
            try:
                message.send(fail_silently=False)
                self.status = 'sent'
                self.save()
            except:
                self.status = 'failed'
                self.save()
        return True

    def __str__(self):
        return '{0} - {1}'.format(self.status, self.subscription)

    class Meta:
        unique_together = ('subscription', 'newsletter')
        ordering = ['status']