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


class Newsletter(Publication):
    """
    This model implements newsletter as a publication.
    """
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