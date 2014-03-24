from django.db import models
from django.core.mail import EmailMultiAlternatives
from publication.models import Publication
from owner.models import Owner

class Subscription(Owner):
    """
    This class holds the newsletter subscribers
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)


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