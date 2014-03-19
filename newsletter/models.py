from django.db import models
from publication.models import Publication
from accounts.models import Owner

class Subscriptions(Owner):
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